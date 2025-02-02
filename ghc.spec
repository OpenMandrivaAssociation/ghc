Summary:	The Glasgow Haskell Compiler
Name:		ghc
Version:	8.2.2
Release:	1
License:	BSD
Group:		Development/Other
Url:		https://haskell.org/ghc/
Source0:	http://haskell.org/ghc/dist/%{version}/ghc-%{version}-src.tar.xz
Source1:	http://haskell.org/ghc/dist/%{version}/ghc-%{version}-testsuite.tar.xz
# Ugly, but GHC requires itself to build. Since we can't rely on
# a previous package, got to bundle upstream's binary packages for now.
Source10:	https://downloads.haskell.org/~ghc/%{version}/ghc-%{version}-i386-deb8-linux.tar.xz
Source11:	https://downloads.haskell.org/~ghc/%{version}/ghc-%{version}-x86_64-deb8-linux-dwarf.tar.xz
Source12:	https://downloads.haskell.org/~ghc/%{version}/ghc-%{version}-armv7-deb8-linux.tar.xz
Source13:	https://downloads.haskell.org/~ghc/%{version}/ghc-%{version}-aarch64-deb8-linux.tar.xz
# RPM integration...
Source20:	haskell.attr
Source21:	haskelldeps.sh
Source22:	haskell.macros

Patch0:		ghc-8.2.2-compile.patch
Patch1:		https://src.fedoraproject.org/rpms/ghc/raw/master/f/D4159.patch
Patch2:		https://src.fedoraproject.org/rpms/ghc/raw/master/f/ghc-Cabal-install-PATH-warning.patch
Patch3:		https://src.fedoraproject.org/rpms/ghc/raw/master/f/ghc-Debian-no-missing-haddock-file-warning.patch
Patch4:		https://src.fedoraproject.org/rpms/ghc/raw/master/f/ghc-Debian-reproducible-tmp-names.patch
Patch5:		https://src.fedoraproject.org/rpms/ghc/raw/master/f/ghc-Debian-x32-use-native-x86_64-insn.patch
Patch6:		https://src.fedoraproject.org/rpms/ghc/raw/master/f/ghc-gen_contents_index-haddock-path.patch
# FIXME we shouldn't do this, it's a workaround for building docs
# barfing. Should fix it properly at some point.
Patch7:		ghc-8.2.2-disable-docs.patch
Requires:	gcc
#BuildRequires:	alex >= 2.0
#BuildRequires:	dblatex
BuildRequires:	docbook-dtd42-xml
#BuildRequires:	ghc
#BuildRequires:	happy >= 1.15
BuildRequires:	texlive
BuildRequires:	texlive-xetex
BuildRequires:	texlive-bibtopic
BuildRequires:	update-alternatives
#BuildRequires:	ghc-devel
BuildRequires:	gmp-devel
BuildRequires:	readline-devel
BuildRequires:	pkgconfig(glut)
BuildRequires:	python-sphinx
BuildRequires:	perl
Requires:	gmp-devel

%description
Haskell is the standard lazy purely functional programming language.
The current language version is Haskell 98, agreed in December 1998,
with a revised version published in January 2003.

GHC is a state-of-the-art programming suite for Haskell. Included is
an optimising compiler generating good code for a variety of
platforms, together with an interactive system for convenient, quick
development. The distribution includes space and time profiling
facilities, a large collection of libraries, and support for various
language extensions, including concurrency, exceptions, and foreign
language interfaces (C, C++, whatever).

A wide variety of Haskell related resources (tutorials, libraries,
specifications, documentation, compilers, interpreters, references,
contact information, links to research groups) are available from the
Haskell home page at http://haskell.org/.

%files -f rpm-noprof-lib-files
%{_mandir}/man1/ghc.1*
%{_bindir}/ghc
%{_bindir}/ghc-%{version}
%{_bindir}/ghc-pkg
%{_bindir}/ghc-pkg-%{version}
%{_bindir}/ghci
%{_bindir}/ghci-%{version}
%{_bindir}/hp2ps
%{_bindir}/hpc
%{_bindir}/hsc2hs
%{_bindir}/hsc2hs-ghc
%{_bindir}/hsc2hs-%{version}
%{_bindir}/runghc
%{_bindir}/runghc-%{version}
%{_bindir}/runhaskell

%{_rpmconfigdir}/fileattrs/haskell.attr
%{_rpmconfigdir}/haskelldeps.sh
%{_sysconfdir}/rpm/macros.d/haskell.macros


%post
# Alas, GHC, Hugs and nhc all come with different set of tools in addition to
# a runFOO:
#
#   * GHC:  hsc2hs
#   * Hugs: hsc2hs, cpphs
#   * nhc:  cpphs
#
# Therefore it is currently not possible to use --slave below to form link
# groups under a single name 'runhaskell'. Either these tools should be
# disentangled from the Haskell implementations or all implementations should
# have the same set of tools. *sigh*
update-alternatives --install %{_bindir}/runhaskell runhaskell %{_bindir}/runghc     500
/usr/bin/ghc-pkg recache

%preun
if test "$1" = 0; then
  update-alternatives --remove runhaskell %{_bindir}/runghc
fi

#----------------------------------------------------------------------------

%package prof
Summary:	Profiling libraries for GHC
Group:		Development/Other
Requires:	%{name} = %{EVRD}

%description prof
Profiling libraries for Glorious Glasgow Haskell Compilation System (GHC).
They should be installed when GHC's profiling subsystem is needed.

%files prof -f rpm-prof-lib-files

#----------------------------------------------------------------------------

%package doc
Summary:	Documentation for the Glasgow Haskell Compiler
Group:		Books/Computer books
Requires:	%{name} = %{EVRD}

%description doc
Documentation for the Glasgow Haskell Compiler.

%files doc
%{_docdir}/%{name}

#----------------------------------------------------------------------------

%package devel
Summary:	GHC development libraries
Group:		Development/Other
Requires:	%{name} = %{EVRD}
Requires:	pkgconfig(libffi)

%description devel
This is a meta-package for all the development library packages in GHC
except the ghc library, which is installed by the toplevel ghc metapackage.

%files devel -f rpm-devel-files

#----------------------------------------------------------------------------

%prep
%setup -q -b1
%autopatch -p1

%ifarch %{ix86}
tar xf %{S:10}
%else
%ifarch x86_64
tar xf %{S:11}
%else
%ifarch %{arm}
tar xf %{S:12}
%else
%ifarch %{armx}
tar xf %{S:13}
%else
echo "ghc needs itself to build. Please find a binary somewhere or port."
exit 1
%endif
%endif
%endif
%endif


%build
TOP="$(pwd)"
cd %{name}-%{version}
./configure --prefix=${TOP}/prebuilt
make install
cd ..
rm -rf %{name}-%{version}
export PATH=${TOP}/prebuilt/bin:${PATH}

# simulate old texlive behavior for processing backslashes in urls in the
# docbooks. see f.e.: http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=563659
export DBLATEX_OPTS="--param=texlive.version=2009"
# makeindex (called by dblatex) by default does not work with absolute paths
export openout_any=r
export CFLAGS="%{optflags}"
# executable-stack rpmlint error
export LDFLAGS="%{optflags} -Wl,-z,noexecstack"

autoreconf -vif
./configure \
	--prefix=%{_prefix} \
	--mandir=%{_mandir} \
	--libdir=%{_libdir} \
	--with-system-libffi \
	--disable-ld-override

cat >mk/build.mk <<'EOF'
BuildFlavour=quick-llvm
EOF

%make

%install
# This is a cruel hack: There seems to be no way to install the Haddock
# documentation into the build directory, because DESTDIR is alway prepended.
# Furthermore, rpm removes the target documentation directory before the doc
# macros are processed. Therefore we have to copy things back into safety... :-P
# The right thing would be being able to install directly into the build tree.
make DESTDIR=%{buildroot} docdir=%{_datadir}/doc/packages/%{name} HADDOCK_DOCS=NO install

mkdir -p %{buildroot}%{_docdir}/%{name}
mv %{buildroot}%{_docdir}/packages/%{name} %{buildroot}%{_docdir}/%{name}/packages
rm -rf %{buildroot}%{_docdir}/packages

mv %{buildroot}%{_prefix}/bin/hsc2hs %{buildroot}%{_prefix}/bin/hsc2hs-%{version}
ln -s hsc2hs-%{version} %{buildroot}%{_prefix}/bin/hsc2hs-ghc
ln -s hsc2hs-%{version} %{buildroot}%{_prefix}/bin/hsc2hs

# RPM integration
install -m644 %{S:20} -D %{buildroot}%{_rpmconfigdir}/fileattrs/haskell.attr
install -m755 %{S:21} -D %{buildroot}%{_rpmconfigdir}/haskelldeps.sh
install -m644 %{S:22} -D %{buildroot}%{_sysconfdir}/rpm/macros.d/haskell.macros

# FIXME continued workaround for not being able to build docs -- let's just steal
# them from the prebuilt version for now...
mkdir -p %{buildroot}%{_mandir}
cp -a prebuilt/share/man/man1 %{buildroot}%{_mandir}
mkdir -p %{buildroot}%{_docdir}/%{name}/html
cp -a prebuilt/share/doc/%{name}-%{version}/html/users_guide %{buildroot}%{_docdir}/%{name}/html/
cp -a prebuilt/share/doc/%{name}-%{version}/users_guide.pdf %{buildroot}%{_docdir}/%{name}/

# generate the file list for lib/ _excluding_ all files needed for profiling
# only
#
# * generating file lists in a BUILD_ROOT spec is a bit tricky: the file list
#   has to contain complete paths, _but_ without the BUILD_ROOT, we also do
#   _not_ want have directory names in the list; furthermore, we have to make
#   sure that any leading / is removed from % {_prefix}/lib, as find has to
#   interpret the argument as a relative path; however, we have to include the
#   leading / again in the final file list (otherwise, rpm complains)
# * isn't there an easier way to do all this?
#
dir=`pwd`
cd %{buildroot}
libdir=`echo %{_libdir} | sed 's|^/||'`
find $libdir ! -type d ! -name '*.p_hi' ! -name '*_p.a' ! -name 'libffi.so*' ! -name '*.a' ! -name '*.h' -print | sed 's|^|/|' > $dir/rpm-noprof-lib-files
find $libdir ! -type d -name '*.p_hi' -print | sed 's|^|/|' > $dir/rpm-prof-lib-files
find $libdir ! -type d \( -name '*.a' -or -name '*.h' \) -print | sed 's|^|/|' > $dir/rpm-devel-files
cd $dir

