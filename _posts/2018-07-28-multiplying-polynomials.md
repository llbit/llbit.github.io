# Multiplying Polynomials with Fast Fourier Transform
<!-- date={2018-07-28} -->

I recently learned a very strange way of multiplying polynomials.

The straightforward way of multiplying two polynomials of degree n takes O(n^2) time: multiply each term from one polynomial with each term from the other.

There is a clever algebraic optimization that has running time O(n^lg3). Explanations of that algorithm can be found [here](https://www.eecis.udel.edu/~saunders/courses/621/99f/p17a/p17.pdf), [here](http://www.cse.ust.hk/~dekai/271/notes/L03/L03.pdf), and [here](https://www.geeksforgeeks.org/multiply-two-polynomials-2/).

Surprisingly, there is a much faster O(n log n) algorithm. Even more surprisingly, the algorithm solves the problem via a completely different mathematical domain by using the Discrete Fourier Transform (DFT). The algorithm works as follows: take the DFT of the input polynomials, point-wise multiply them together, then take the inverse DFT to get the result. Plain DFT is not fast enough, taking O(n^2) time, but the Fast Fourier Transform (FFT) can be used instead and it takes only time O(n log n). Point-wise multiplication takes time O(n), so the total running time is O(n log n)!

![Book cover: Introduction to Algorithms, Second Edition.](/assets/intro_alg.jpg)

A detailed explanation of the FFT-based algorithm can be found in *Introduction to Algoithms, Second Edition,* by Cormen, Leiserson, Rivest, and Stein (Chapter 30). The best and most complete description I've read is the one from the book, but there are a few resources online: like [these lecture notes](http://web.cecs.pdx.edu/~maier/cs584/Lectures/lect07b-11-MG.pdf) which summarize/copy material from the book.

[Fourier Transforms](https://en.wikipedia.org/wiki/Fourier_transform) are normally used for digital signal processing applications (image, audio processing). The Fourier Transform breaks up a signal into its individual frequencies. Polynomial multiplication, on the other hand, is a form of combinatorial problem. Learning that we can use FFT to multiply polynomials makes me wonder if FFT can be used to speed up other problems in combinatorics.

