# Linux ASLR update crashes AddressSanitizer
<!-- date={2024-03-19} -->

I had some C code randomly start crashing on my Ubuntu laptop yesterday.
The code was previously working fine but it started crashing with AddressSanitizer
infinitely printing `AddressSanitizer:DEADLYSIGNAL` in the console.

The first thing I did was to try to narrow down the cause within my own code,
so I stripped out parts of it to find the faulty code.
This process was slightly complicated by the fact that the program
was not reliably crashing - often it would run just fine but about 1/4 or
1/5 of the times it was started it crashed immediately.

I had soon removed all of the code in the program and ended up with just an
empty `main` function.  In fact at this point I could reliably reproduce the
error by running this one-liner in the terminal:

```bash
echo "int main() {}" | gcc -fsanitize=address -xc - && for i in {1..100}; do ./a.out; done
```

The for-loop made the crash reliably appear at least once every time the command was
run.

At this point I started to suspect a package update on my system was at fault.
Long story short, it turns out that a change to the address-space layout
randomization (ASLR) in the Ubuntu-packaged Linux kernel version 6.5.0-25
caused the issue. As far as I can tell kernel versions before that build used 28 random bits
on 64-bit systems and the change upped it to the maximum possible which was 32.

The exact change is documented in the [changelog for Ubuntu package linux
6.5.0-25.25](https://launchpad.net/ubuntu/+source/linux/6.5.0-25.25)

```
  * test_021_aslr_dapper_libs from ubuntu_qrt_kernel_security failed on K-5.19 /
    J-OEM-6.1 / J-6.2 AMD64 (LP: #1983357)
    - [Config]: set ARCH_MMAP_RND_{COMPAT_, }BITS to the maximum
```

The AddressSanitizer library needs to be configured to accommodate for the
number of ASLR bits used on the system and the Ubuntu LLVM distribution has not
yet been updated to match the kernel ASLR configuration.

There are several different issues on various open source issue trackers on the
net discussing this issue and [a bug has been reported to the main Ubuntu issue
tracker](https://bugs.launchpad.net/ubuntu/+source/linux/+bug/2056762) so it is
very likely that this will be fixed soon.

## Workaround

At the moment I am using the following workaround to temporarily set the ASLR
bit count back to 28:

```bash
sudo sysctl -w vm.mmap_rnd_bits=28
```

This change is reset on reboot but I seldom do reboot so I'll live with
this until the LLVM packages are updated by Ubuntu to adjust for the ASLR
change in the kernel.
