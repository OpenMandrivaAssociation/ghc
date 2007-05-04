%define _enable_debug_packages %{nil}
%define debug_package          %{nil}

Name:		ghc
Version:	6.6.1
Release:	%mkrel 1
Summary:	Glasgow Haskell Compilation system
License:	BSD style
Group:		Development/Other
Source:		http://www.haskell.org/ghc/dist/%{version}/ghc-%{version}-src.tar.bz2
Source1:	http://www.haskell.org/ghc/dist/%{version}/ghc-%{version}-src-extralibs.tar.bz2
# fix installation pat on x86_64
Patch1:		ghc-lib64.patch
URL:		http://haskell.org/ghc/
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root
BuildRequires:	gmp-devel, readline-devel, flex, perl, docbook-utils
BuildRequires:	ghc
BuildRequires:	ncurses-devel
#BuildRequires:	libMesaglut-devel
BuildRequires:	gcc
BuildRequires:	haddock >= 0.8
BuildRequires:	happy, alex
BuildRequires:	libxslt-proc, docbook-style-xsl
#BuildRequires: openal-devel
Requires:	gcc
Epoch:		0
# this is not an error, you need need to link application
Requires: gmp-devel
Provides: haskell-compiler = %{version}
Provides: haskell-interactive = %{version}
BuildRequires: haskell-macros >= 6.0

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

%if "%{_lib}" != "lib"
%patch1 
%endif

%build
#%ifarch x86_64
#echo "GhcUnregisterised=YES" > mk/build.mk
#echo "SplitObjs=NO" >> mk/build.mk
#%endif
# disable OpenAL : it breaks build :-(  --disable-openal
./configure --prefix=%{_prefix} --libdir=%{_libdir} --disable-alut

make  CFLAGS="$RPM_OPT_FLAGS"
make html

%install
rm -rf $RPM_BUILD_ROOT

make prefix=$RPM_BUILD_ROOT%{_prefix} libdir=$RPM_BUILD_ROOT%{_libdir}/ghc-%{version} install
make datadir=`pwd` mandir=${RPM_BUILD_ROOT}%{_mandir} install-docs                                           

SRC_TOP=$PWD
rm -f rpm-*.files
( cd $RPM_BUILD_ROOT
  find .%{_libdir} \( -type f \( -name '*.p_hi' -o -name '*_p.a' \) -fprint $SRC_TOP/rpm-prof.files \) -o \( -type f -not -name 'package.conf' -fprint $SRC_TOP/rpm-ghc.files \)
  sed -i '/%{_lib}$/d' $SRC_TOP/rpm-ghc.files
)

# make paths absolute (filter "./usr" to "/usr")
perl -pi -e "s|\.%{_prefix}|%{_prefix}|" rpm-*.files

# Haskell Provides, ugly way, we can't trust .cabal
mkdir -p %buildroot%_cabal_pkg_deps_dir
touch %buildroot%_cabal_pkg_deps_dir/{provides,requires}

./utils/ghc-pkg/ghc-pkg -f ./driver/package.conf list --simple-output | \
    grep ghc-%{version} | \
    perl -p -e 's/ *([\w-]*)-([^-, ]*)[, ]*/haskell($1) = $2\n/g' | sort | uniq \
    > %buildroot%_cabal_pkg_deps_dir/provides

%clean
rm -rf $RPM_BUILD_ROOT

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
%doc html


