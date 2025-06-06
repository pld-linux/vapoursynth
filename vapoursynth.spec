#
# Conditional build:
%bcond_without	doc		# documentation
%bcond_with	sse		# use SSE/SSE2 instructions on x86 (no runtime detection)
%bcond_without	static_libs	# static libraries
#
%ifarch pentium4 %{x8664}
# x32 asm is not supported (as of 38)
%define	with_sse	1
%endif
Summary:	A video processing framework with simplicity in mind
Summary(pl.UTF-8):	Szkielet do przetwarzania obrazu stworzony z myślą o prostocie
Name:		vapoursynth
Version:	72
Release:	1
License:	LGPL v2.1+
Group:		Libraries
#Source0Download: https://github.com/vapoursynth/vapoursynth/releases
Source0:	https://github.com/vapoursynth/vapoursynth/archive/R%{version}/%{name}-R%{version}.tar.gz
# Source0-md5:	e8dc8f3d327805b0a893c65c1a772745
Patch0:		%{name}-sse2.patch
URL:		http://www.vapoursynth.com/
BuildRequires:	autoconf >= 2.50
BuildRequires:	automake >= 1:1.11
BuildRequires:	libstdc++-devel >= 6:7
BuildRequires:	libtool >= 2:2
%if %{with sse}
BuildRequires:	nasm
%endif
BuildRequires:	pkgconfig
BuildRequires:	python3-Cython
BuildRequires:	python3-devel >= 1:3.2
BuildRequires:	rpm-build >= 4.6
BuildRequires:	rpmbuild(macros) >= 1.752
BuildRequires:	sed >= 4.0
BuildRequires:	zimg-devel >= 3.0.5
%if %{with doc}
BuildRequires:	python3-sphinx_rtd_theme
BuildRequires:	sphinx-pdg-3
%endif
%if %{with sse}
Requires:	cpuinfo(sse2)
%endif
Requires:	python3-libs >= 1:3.2
Requires:	zimg >= 3.0.5
Obsoletes:	vapoursynth-plugin-imwri < 54-5
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

# non-function std::__once_call, std::__once_callable symbols
%define		skip_post_check_so	libvapoursynth-script.so.*

%description
VapourSynth is an application for video manipulation. Or a plugin. Or
a library. It's hard to tell because it has a core library written in
C++ and a Python module to allow video scripts to be created.

%description -l pl.UTF-8
VapourSynth to aplikacja do obróbki obrazu. Albo wtyczka. Albo
biblioteka. Trudno stwierdzić, ponieważ ma główną bibliotekę napisaną
w C++ oraz moduł Pythona pozwalający na tworzenie skryptów do obrazu.

%package devel
Summary:	Header files for VapourSynth libraries
Summary(pl.UTF-8):	Pliki nagłówkowe bibliotek VapourSynth
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}
Requires:	python3-devel >= 1:3.2
Requires:	zimg-devel >= 3.0.5

%description devel
Header files for VapourSynth libraries.

%description devel -l pl.UTF-8
Pliki nagłówkowe bibliotek VapourSynth.

%package static
Summary:	Static VapourSynth libraries
Summary(pl.UTF-8):	Statyczne biblioteki VapourSynth
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}

%description static
Static VapourSynth libraries.

%description static -l pl.UTF-8
Statyczne biblioteki VapourSynth.

%package doc
Summary:	Documentation for VapourSynth library
Summary(pl.UTF-8):	Dokumentacja do biblioteki VapourSynth
Group:		Documentation
BuildArch:	noarch

%description doc
Documentation for VapourSynth library.

%description doc -l pl.UTF-8
Dokumentacja do biblioteki VapourSynth.

%prep
%setup -q -n %{name}-R%{version}
%patch -P 0 -p1

%if %{without sse}
%{__sed} -i -e 's/"-mfpmath=sse -msse2"/""/' configure.ac
%endif

%build
%{__libtoolize}
%{__aclocal}
%{__autoconf}
%{__automake}
%configure \
	--disable-silent-rules \
	%{!?with_static_libs:--disable-static} \
	%{!?with_sse:--disable-x86-asm}
%{__make}

%if %{with doc}
sphinx-build-3 -b html doc doc/_build/html
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_libdir}/vapoursynth

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

%{__rm}	$RPM_BUILD_ROOT%{py3_sitedir}/vapoursynth.la
# obsoleted by pkg-config
%{__rm} $RPM_BUILD_ROOT%{_libdir}/libvapoursynth*.la

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc ChangeLog README.md
%attr(755,root,root) %{_bindir}/vspipe
%attr(755,root,root) %{_libdir}/libvapoursynth.so
%attr(755,root,root) %{_libdir}/libvapoursynth-script.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libvapoursynth-script.so.0
%attr(755,root,root) %{py3_sitedir}/vapoursynth.so
%dir %{_libdir}/vapoursynth

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libvapoursynth-script.so
%{_includedir}/vapoursynth
%{_pkgconfigdir}/vapoursynth.pc
%{_pkgconfigdir}/vapoursynth-script.pc

%if %{with static_libs}
%files static
%defattr(644,root,root,755)
%{_libdir}/libvapoursynth.a
%{_libdir}/libvapoursynth-script.a
%endif

%if %{with doc}
%files doc
%defattr(644,root,root,755)
%doc doc/_build/html/{_static,functions,*.html,*.js}
%endif
