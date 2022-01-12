# Building a Standalone Clang Tool
<!-- date={2023-12-01} -->

I wrote a small Clang-based tool to analyze C code to find potentially
problematic assign-through pointer expressions.
The assignments I want to find look like this: `PTR(x)->y = z` where
`PTR` is a macro that dereferences some pointer expression `x`.
As the order in which the left- and right-hand sides
of an assignment are evaluated in C is undefined this could lead to memory
errors if the `z` expression contains side effects that affect pointer derferenced in
the left-hand side.

The code I'm analyzing is a lare C project project that uses its own garbage
collector (GC) where `PTR` is a macro for dereferencing a GC object.  There
were some bugs caused in our test suite by through-pointer assignments like the
above one when when running the tests on an ARM-based platform (the bug did not
occur in the normal x86-based test environment).

## Clang AstMatcher API

Finding these kinds of expressions with Clang is pretty easy. Clang has an API
for AST matching that [allows us to write matchers such as this:](AstMatcher Tutorial)

```c++
auto AssignMatcher = binaryOperator(
    hasOperatorName("="),
    hasLHS(memberExpr(hasObjectExpression(stmt(isExpandedFromMacro("PTR"))))),
    hasRHS(findAll(callExpr()))
  );
```

This matcher finds all expressions as described above where the right-hand side
additionally contains a function call.

Running my tool on each continuous integration build would ensure that we don't
encounter this particular type of bug again in the project.

## Building Standalone

Although my tool was pretty simple, with less than 100 lines of code, figuring out how to
build it proved to be more challenging that just writing the tool itself.

Although it is possible to compile a Clang tool using [LibTooling](LibTooling)
against pre-built LLVM/Clang binaries that are available in Debian, e.g.,
this is not really covered in the LLVM documentation.

Most pages in the documentation at `llvm.org` assume that you've built LLVM
from source, rather than using pre-built binaries.

I tried building LLVM from source on my laptop at first but quickly gave up
when the build soon ran out of memory.  It turns out that you need about 30-40 GB of
working memory and about 120 GB of free disk space to build the current
latest version of LLVM (17.0.6).  If you don't have enough RAM you
have to rely on Swap space.  The source code takes about 2 GB of space if
downloaded as a shallow Git clone and the build directory of a completed build
on my machine was 113 GB.

In the end I did manage to build my tool against the pre-built LLVM-15 Debian
packages although finding out how to correctly link the code was tricky.  [The
tool `llvm-config` can be used to generate compiler flags for compiling/linking
a standalone tool](llvm-config) but I did not know where to find the list of
LLVM components I needed to link with.

I tried to link against all 90 `libclang*.a` files in `/usr/lib/llvm-15/lib`,
however, that failed with lots of undefined symbol errors from the linker. This
seemed strange as using `nm` turned up matching symbols in those libraries.  It
turns out that the LLVM libraries have circular dependencies and to solve these
the linker will have to iteratively resolve names among the libraries.

Normally the linker only does one pass over the listed libraries which then
fails on the first undefined symbol. To handle circular references
one can use the `-Wl,--start-group` and `-Wl,--end-group` flags surrounding the
list of libraries that contain circular references
This solved the linking problems so I was finally able to
link my tool. I narrowed down the list of libraries a bit and ended up with the
following magical incantation:

```
g++ -g `llvm-config-15 --cxxflags` -o tool.o -c tool.cc
g++ -g `llvm-config-15 --ldflags` -o tool tool.o \
    -Wl,--start-group \
    -lclang -lclangSupport -lclangAST -lclangASTMatchers \
    -lclangFrontend -lclangDriver -lclangParse -lclangSerialization \
    -lclangSema -lclangAnalysis -lclangEdit -lclangAST -lclangLex -lclangBasic \
    -lclangTooling -lclangToolingCore -lclangToolingSyntax -lclangToolingASTDiff \
    -lclangRewrite \
    -Wl,--end-group \
    `llvm-config-15 --libs engine`
```

## Outdated Documentation

The [LibTooling](LibTooling) page contains an outdated example code snippet:

```c++
int main(int argc, const char **argv) {
  CommonOptionsParser OptionsParser(argc, argv, MyToolCategory);
  ClangTool Tool(OptionsParser.getCompilations(),
                 OptionsParser.getSourcePathList());
  return Tool.run(newFrontendActionFactory<clang::SyntaxOnlyAction>().get());
}
```

The `CommonOptionsParser` class should not be instantiated directly. It has
been made protected in some previous version of LLVM.  Instead the builder
function `::create` should be called:

```c++
int main(int argc, const char **argv) {
  auto Options = CommonOptionsParser::create(argc, argv, PtrAssCategory);
  ClangTool Tool(Options->getCompilations(), Options->getSourcePathList());
}
```

## Putting it all Together

Here is the full code of an initial version of my tool.  The code compiles
against LLVM 15.0.7 and may not work with other versions.

I've made some improvements to the tool which are not included but it should
work as a starting point if you are looking to make a similar Clang tool.

```c++
#include "clang/ASTMatchers/ASTMatchFinder.h"
#include "clang/ASTMatchers/ASTMatchers.h"
#include "clang/Frontend/FrontendActions.h"
#include "clang/Frontend/FrontendPluginRegistry.h"
#include "clang/Frontend/TextDiagnostic.h"
#include "clang/Frontend/TextDiagnosticPrinter.h"
#include "clang/Frontend/CompilerInstance.h"
#include "clang/Rewrite/Core/Rewriter.h"
#include "clang/Tooling/CommonOptionsParser.h"
#include "clang/Tooling/Tooling.h"
#include "llvm/Support/CommandLine.h"
#include "llvm/Support/Signals.h"

using namespace clang;
using namespace clang::ast_matchers;
using namespace clang::Builtin;
using namespace clang::tooling;
using namespace llvm;
using namespace llvm::cl;

auto AssignMatcher = binaryOperator(
    hasOperatorName("="),
    hasLHS(memberExpr(hasObjectExpression(stmt(isExpandedFromMacro("PTR"))))),
    hasRHS(findAll(callExpr()))
  ).bind("assign");

class AssignPrinter : public MatchFinder::MatchCallback {
public:
  virtual void run(const MatchFinder::MatchResult& Result) final {
    if (const BinaryOperator* Node = Result.Nodes.getNodeAs<BinaryOperator>("assign")) {
      DiagnosticsEngine& DE = Result.Context->getDiagnostics();
      auto ID = DE.getCustomDiagID(DiagnosticsEngine::Error,
          "Possibly unsafe assign-through pointer operation. Side-effects in RHS may move object dereferenced in LHS.");
      auto DB = DE.Report(Node->getExprLoc(), ID);
      DB.AddSourceRange(CharSourceRange::getTokenRange(Node->getSourceRange()));
    }
  }
};

static OptionCategory PtrAssCategory("ptr-ass options");
static extrahelp CommonHelp(CommonOptionsParser::HelpMessage);
static extrahelp MoreHelp("ptr-ass finds potentially problematic assign-through pointer expressions\n");

int main(int argc, const char **argv) {
  auto Options = CommonOptionsParser::create(argc, argv, PtrAssCategory);
  if (!Options) {
    llvm::errs() << "No source files specified.\n";
    return -1;
  }
  ClangTool Tool(Options->getCompilations(), Options->getSourcePathList());

  AssignPrinter Printer;
  MatchFinder Finder;
  Finder.addMatcher(AssignMatcher, &Printer);

  return Tool.run(newFrontendActionFactory(&Finder).get());
}
```


[LibTooling]: https://clang.llvm.org/docs/LibTooling.html
[AstMatcher Tutorial]: https://clang.llvm.org/docs/LibASTMatchersTutorial.html
[llvm-config]: https://llvm.org/docs/CommandGuide/llvm-config.html
