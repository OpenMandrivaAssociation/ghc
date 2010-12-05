%define _enable_debug_packages %{nil}
%define debug_package          %{nil}

Name:		ghc
Version:	6.10.4
Release:	%mkrel 4
Summary:	Glasgow Haskell Compilation system
License:	BSD style
Group:		Development/Other
Source:		http://www.haskell.org/ghc/dist/%{version}/ghc-%{version}-src.tar.bz2
Source1:	http://www.haskell.org/ghc/dist/%{version}/ghc-%{version}-src-extralibs.tar.bz2
URL:		http://haskell.org/ghc/
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root
BuildRequires:	gmp-devel, readline-devel, flex, perl, docbook-utils
BuildRequires:	ghc
BuildRequires:	ncurses-devel
#BuildRequires:	mesaglut-devel
BuildRequires:	gcc
#BuildRequires:	haddock >= 0.8
BuildRequires:	happy, alex
BuildRequires:	libxslt-proc, docbook-style-xsl
#BuildRequires: openal-devel
Requires:	gcc
Epoch:		0
# this is not an error, you need need to link application
Requires:	gmp-devel
Provides:	haskell-compiler = %{version}
Provides:	haskell-interactive = %{version}
Obsoletes:	haskell-filepath < 1.1.0.2
BuildRequires:	haskell-macros >= 6.0

%description
GHC is a state-of-the-art programming suite for Haskell, a purely
functional programming language.  It includes an optimising compiler
generating good code for a variety of platforms, together with an
interactive system for convenient, quick development.  The
distribution includes space and time profiling facilities, a large
collection of libraries, and support for various language
extensions, including concurrency, exceptions, and foreign language
interfaces (C, C++, etc).

%package -n ghc-prof
Summary:	Profiling libraries for GHC
Group:		Development/Other
Requires:	ghc = %{epoch}:%{version}-%{release}

%description -n ghc-prof
Profiling libraries for Glorious Glasgow Haskell Compilation System
(GHC).  They should be installed when GHC's profiling subsystem is
needed.

%package doc
Summary:        GHC docs
Group:          Development/Other

%description doc
GHC is a state-of-the-art programming suite for Haskell, a purely
functional programming language.  It includes an optimising compiler
generating good code for a variety of platforms, together with an
interactive system for convenient, quick development.  The
distribution includes space and time profiling facilities, a large
collection of libraries, and support for various language
extensions, including concurrency, exceptions, and foreign language
interfaces (C, C++, etc).

%define __spec_install_post /usr/lib/rpm/brp-compress

%prep
%setup -q -b 1 -n ghc-%{version}

# Fix path for module
perl -pi -e 's/"lib"/"%_lib"/' libraries/Cabal/Distribution/Simple/InstallDirs.hs

%build
#%ifarch x86_64
#echo "GhcUnregisterised=YES" > mk/build.mk
#echo "SplitObjs=NO" >> mk/build.mk
#%endif
# disable OpenAL : it breaks build :-(  --disable-openal
./configure --prefix=%{_prefix} --libdir=%{_libdir} --disable-alut

%make  CFLAGS="%{optflags}"
make html

%install
rm -rf %{buildroot}

make DESTDIR=%{buildroot} \
    "DO_NOT_INSTALL=pwd installPackage haddock" \
    install

echo %{_docdir}

make DESTDIR=%{buildroot} \
    docdir=%{_docdir}/%{name} \
    mandir=%{_mandir} install-docs

SRC_TOP=$PWD
rm -f rpm-*.files
( cd %{buildroot}
  find .%{_libdir} \( -type f \( -name '*.p_hi' -o -name '*_p.a' \) -fprint $SRC_TOP/rpm-prof.files \) -o \( -type f -not -name 'package.conf' -fprint $SRC_TOP/rpm-ghc.files \)
  sed -i '/%{_lib}$/d' $SRC_TOP/rpm-ghc.files
)

# make paths absolute (filter "./usr" to "/usr")
perl -pi -e "s|\.%{_prefix}|%{_prefix}|" rpm-*.files

# Haskell Provides, ugly way, we can't trust .cabal
mkdir -p %buildroot%_cabal_pkg_deps_dir
touch %buildroot%_cabal_pkg_deps_dir/{provides,requires}

# Haskell magic provides
./utils/ghc-pkg/dist-install/build/ghc-pkg/ghc-pkg \
    list --simple-output \
    --global-conf=./inplace-datadir/package.conf \
    | perl -p -e 's/ *([\w-]*)-([^-, ]*)[, ]*/haskell($1) = $2\n/g' \
    | sort | uniq \
    > %buildroot%_cabal_pkg_deps_dir/provides

%check

grep haskell98 %buildroot%_cabal_pkg_deps_dir/provides >/dev/null
if [ $? -ne 0 ] ; then
    echo "I cannot find basic provides in %buildroot%_cabal_pkg_deps_dir/provides"
    echo "Please check..."
    exit 1
fi 

%clean
rm -rf %{buildroot}

%files -f rpm-ghc.files
%defattr(-,root,root,-)
%{_bindir}/*
%dir %{_libdir}/ghc-%{version}
#- TODO move this under /etc or don't flag it as config file
%config %{_libdir}/ghc-%{version}/package.conf
%doc ANNOUNCE LICENSE README
%doc HACKING
%{?_cabal_rpm_files}
%{_mandir}/man1/*

%files -n ghc-prof -f rpm-prof.files
%defattr(-,root,root,-)

%files doc
%doc %_docdir

