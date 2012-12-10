Name:           ghc
Version:        7.6.1
Release:        7
License:        BSD
Group:          Development/Other
URL:            http://haskell.org/ghc/
Source0:        http://haskell.org/ghc/dist/%{version}/ghc-%{version}-src.tar.bz2
patch0:         ghc-7.6.1-haddockpath.patch
patch1:         ghc-7.6.1-fromsuse-use-system-libffi.patch
Requires:       gcc
BuildRequires:  update-alternatives
buildrequires:  alex >= 2.0
buildrequires:  happy >= 1.15
buildrequires:  ghc >= 5
#buildrequires:  docbook-utils
#buildrequires:  docbook-style-xsl
buildrequires:  docbook-dtd42-xml
#buildrequires:  pkgconfig(libexslt)
#buildrequires:  libxml2
#buildrequires:  fop
#buildrequires:  xmltex
buildrequires:  gmp-devel
buildrequires:  readline-devel
buildrequires:  pkgconfig(glut)
buildrequires:  dblatex
buildrequires:  texlive-bibtopic
buildrequires:  ghc-devel
requires:       gmp-devel

Summary:        The Glasgow Haskell Compiler

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

Authors:
--------
    Krasimir Angelov <ka2_mail@yahoo.com>
    Manuel Chakravarty <chak@cse.unsw.edu.au>
    Koen Claessen <koen@cs.chalmers.se>
    Robert Ennals <Robert.Ennals@cl.cam.ac.uk>
    Sigbjorn Finne <sof@galconn.com>
    Gabrielle Keller <keller@cvs.haskell.org>
    Marcin Kowalczyk <qrczak@knm.org.pl>
    Jeff Lewis <jeff@galconn.com>
    Ian Lynagh <igloo@earth.li>
    Simon Marlow <simonmar@microsoft.com>
    Sven Panne <sven.panne@aedion.de>
    Ross Paterson <ross@soi.city.ac.uk>
    Simon Peyton Jones <simonpj@microsoft.com>
    Don Stewart <dons@cse.unsw.edu.au>
    Volker Stolz <stolz@i2.informatik.rwth-aachen.de>
    Wolfgang Thaller <wolfgang.thaller@gmx.net>
    Andrew Tolmach <apt@cs.pdx.edu>
    Keith Wansbrough <Keith.Wansbrough@cl.cam.ac.uk>
    Michael Weber <michael.weber@post.rwth-aachen.de>
    plus a dozen helping hands...

%package prof
Requires:       %{name} = %{version}-%{release}
Summary:        Profiling libraries for GHC
Group:          Development/Other

%description prof
Profiling libraries for Glorious Glasgow Haskell Compilation System
(GHC).  They should be installed when GHC's profiling subsystem is
needed.

%package doc
Summary: Documentation for the Glasgow Haskell Compiler
Group:   Books/Computer books
Requires: %{name} = %{version}-%{release}
requires: locales-doc

%description doc
Documentation for the Glasgow Haskell Compiler

%package devel
Summary:     GHC development libraries
Group:       Development/Other
Requires:    %{name} = %{version}-%{release}
requires:    pkgconfig(libffi)

%description devel
This is a meta-package for all the development library packages in GHC
except the ghc library, which is installed by the toplevel ghc metapackage.


%prep
%setup -q
%patch0 -p1 -b .haddockpath
%patch1 -p1 -b .use-system-libffi

%build
# simulate old texlive behavior for processing backslashes in urls in the
# docbooks. see f.e.: http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=563659
export DBLATEX_OPTS="--param=texlive.version=2009"
# makeindex (called by dblatex) by default does not work with absolute paths
export openout_any=r
# executable-stack rpmlint error
export LDFLAGS="-Wl,-z,noexecstack"

autoreconf -vif
./configure --prefix=%{_prefix} --mandir=%{_mandir} --libdir=%{_libdir} \
	--with-system-libffi

# Don't install these tools, we'll use update-alternatives below.
touch mk/build.mk
echo "NO_INSTALL_RUNHASKELL=YES" >>mk/build.mk
echo "NO_INSTALL_HSC2HS=YES" >>mk/build.mk

make %{?jobs:-j%jobs}
#make html
# Alas, we don't pass make options/arguments down to "libraries", so let's redo make here...
#make -C libraries HADDOCK_DOCS=YES
#( cd libraries/Cabal && docbook2html doc/Cabal.xml --output doc/Cabal ) || echo "haha cd libraries"
#make -C docs/ext-core ps
#make -C docs/storage-mgt ps

%install
# This is a cruel hack: There seems to be no way to install the Haddock
# documentation into the build directory, because DESTDIR is alway prepended.
# Furthermore, rpm removes the target documentation directory before the doc
# macros are processed. Therefore we have to copy things back into safety... :-P
# The right thing would be being able to install directly into the build tree.
make DESTDIR=${RPM_BUILD_ROOT} docdir=%{_datadir}/doc/packages/%{name} HADDOCK_DOCS=NO install
#make DESTDIR=${RPM_BUILD_ROOT} docdir=% {_datadir}/doc/packages/% {name} HADDOCK_DOCS=YES install-docs

#mkdir html-docs
#cp -a ${RPM_BUILD_ROOT}% {_datadir}/doc/packages/% {name}/html/{index.html,libraries} html-docs

mkdir -p %{buildroot}%{_docdir}/%{name}
mv %{buildroot}%{_docdir}/packages/%{name} %{buildroot}%{_docdir}/%{name}/packages
rm -rf %{buildroot}%{_docdir}/packages

mv ${RPM_BUILD_ROOT}%{_prefix}/bin/hsc2hs ${RPM_BUILD_ROOT}%{_prefix}/bin/hsc2hs-%{version}
ln -s hsc2hs-%{version} ${RPM_BUILD_ROOT}%{_prefix}/bin/hsc2hs-ghc
ln -s hsc2hs-%{version} ${RPM_BUILD_ROOT}%{_prefix}/bin/hsc2hs

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
cd ${RPM_BUILD_ROOT}
libdir=`echo %{_libdir} | sed 's|^/||'`
find $libdir ! -type d ! -name '*.p_hi' ! -name '*_p.a' ! -name 'libffi.so*' ! -name '*.a' ! -name '*.h' -print | sed 's|^|/|' > $dir/rpm-noprof-lib-files
find $libdir ! -type d -name '*.p_hi' -print | sed 's|^|/|' > $dir/rpm-prof-lib-files
find $libdir ! -type d \( -name '*.a' -or -name '*.h' \) -print | sed 's|^|/|' > $dir/rpm-devel-files
cd $dir

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
#update-alternatives --install %{_bindir}/hsc2hs     hsc2hs     %{_bindir}/hsc2hs-ghc 500
/usr/bin/ghc-pkg recache

%preun
if test "$1" = 0; then
  update-alternatives --remove runhaskell %{_bindir}/runghc
#  update-alternatives --remove hsc2hs     %{_bindir}/hsc2hs-ghc
fi

%files doc
%defattr(-,root,root)
%doc docs/comm
%{_docdir}/%{name}

%files -f rpm-noprof-lib-files
%defattr(-,root,root)
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

%files prof -f rpm-prof-lib-files
%defattr(-,root,root)

%files devel -f rpm-devel-files
%defattr(-,root,root)
