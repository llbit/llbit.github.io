# Fixing my Toilet with 3D Printing
<!-- date={2024-09-22} -->

A small plastic pin inside the hinge on the seat of my toilet broke. I figured I could print a replacement part with my 3D printer,
so I measured the original part and modeled it in FreeCAD. The first iteration looked like this:

![Design version 1 in FreeCAD](/assets/hinge1.jpg)

This design closely matched the original part and was functional but it had some issues. First of all, it's not very
nice to 3D print. If you are familiar with 3D printing you probably already spotted the issue: being a long part with no good surface to lie flat on thus requiring support material.

![Version 1 sliced](/assets/hinge1slice.jpg)

The bigger issue with the design however are those thin teeth at the end. Those teeth are intended to flex when inserting the pin in the hinge, but they are too thin and the plastic
I printed the part in was too brittle so after a couple weeks the teeth broke off and the hinge fell apart again.
So I went back to the drawing table and realized I had to make those teeth more robust. This is what I came up with:

![Design version 2 in FreeCAD](/assets/hinge2.jpg)
![Version 2 sliced](/assets/hinge2slice.jpg)

Now the teeth are much stronger but still allow flexing so that the pin can be inserted into the hinge. This second design worked great. To improve the printing of the part I also made
a flat surface along the length of the part. This might make the part marginally more bendy but it certainly improved the print quality. Here are the new parts installed in the hinges:

![Version 2 sliced](/assets/hinge2toilet.jpg)
