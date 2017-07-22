#
# Conditional build:
%bcond_without	doc		# documentation
%bcond_without	ffmpeg		# subtext plugin (libass+ffmpeg based)
%bcond_with	sse		# use SSE/SSE2 instructions on x86 (no runtime detection)
%bcond_without	static_libs	# static libraries
#
%ifarch pentium4 %{x8664} x32
%define	with_sse	1
%endif
Summary:	A video processing framework with simplicity in mind
Summary(pl.UTF-8):	Szkielet do przetwarzania obrazu stworzony z myślą o prostocie
Name:		vapoursynth
Version:	38
Release:	1
License:	LGPL v2.1+
Group:		Libraries
#Source0Download: https://github.com/vapoursynth/vapoursynth/releases
Source0:	https://github.com/vapoursynth/vapoursynth/archive/R%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	78d0183f0afd3702f3edc176b2491f5d
Patch0:		%{name}-genericarch.patch
URL:		http://www.vapoursynth.com/
BuildRequires:	ImageMagick-c++-devel >= 1:7
BuildRequires:	autoconf >= 2.50
BuildRequires:	automake >= 1:1.11
# libavcodec libavformat libavutil
%{?with_ffmpeg:BuildRequires:	ffmpeg-devel}
%{?with_ffmpeg:BuildRequires:	libass-devel}
BuildRequires:	libstdc++-devel >= 6:4.8
BuildRequires:	libtool >= 2:2
BuildRequires:	pkgconfig
BuildRequires:	python3-Cython
BuildRequires:	python3-devel >= 1:3.2
BuildRequires:	sed >= 4.0
%{?with_doc:BuildRequires:	sphinx-pdg}
BuildRequires:	tesseract-devel >= 3
%if %{with sse}
BuildRequires:	yasm
%endif
BuildRequires:	zimg-devel >= 2.5
%if %{with sse}
Requires:	cpuinfo(sse2)
%endif
Requires:	python3-libs >= 1:3.2
Requires:	zimg >= 2.5
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

# non-function std::__once_call, std::__once_callable symbols
%define		skip_post_check_so	libvapoursynth-script.so.*

%description
VapourSynth is an application for video manipulation. Or a plugin. Or
a library. It's hard to tell  because it has a core library written in
C++ and a Python module to allow video scripts to be created.

%description -l pl.UTF-8
VapourSynth to aplikacja do obróbki obrazu. Albo wtyczka. Albo
biblioteka. Trudno stwierdzić, ponieważ ma główną bibliotekę napisaną
w C++ oraz moduł Pythona pozwalający na tworzenie skryptów do obrazu.

%package plugin-imwri
Summary:	Image reader/writer plugin for VapourSynth
Summary(pl.UTF-8):	Wtyczka VapourSynth odczytująca i zapisują obrazy
Group:		Libraries
Requires:	%{name} = %{version}-%{release}

%description plugin-imwri
Image reader/writer plugin for VapourSynth.

%description plugin-imwri -l pl.UTF-8
Wtyczka VapourSynth odczytująca i zapisują obrazy.

%package plugin-ocr
Summary:	OCR plugin for VapourSynth
Summary(pl.UTF-8):	Wtyczka OCR dla VapourSyntha
Group:		Libraries
Requires:	%{name} = %{version}-%{release}

%description plugin-ocr
OCR plugin for VapourSynth.

%description plugin-ocr -l pl.UTF-8
Wtyczka OCR dla VapourSyntha.

%package plugin-subtext
Summary:	Subtitle rendering plugin for VapourSynth
Summary(pl.UTF-8):	Wtyczka VapourSynth nanosząca podpisy
Group:		Libraries
Requires:	%{name} = %{version}-%{release}

%description plugin-subtext
Subtitle rendering plugin for VapourSynth.

%description plugin-subtext -l pl.UTF-8
Wtyczka VapourSynth nanosząca podpisy.

%package devel
Summary:	Header files for VapourSynth libraries
Summary(pl.UTF-8):	Pliki nagłówkowe bibliotek VapourSynth
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}
Requires:	python3-devel >= 1:3.2
Requires:	zimg-devel >= 2.5

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
%if "%{_rpmversion}" >= "5"
BuildArch:	noarch
%endif

%description doc
Documentation for VapourSynth library.

%description doc -l pl.UTF-8
Dokumentacja do biblioteki VapourSynth.

%prep
%setup -q -n %{name}-R%{version}
%patch0 -p1

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
	%{!?with_ffmpeg:--disable-subtext} \
	%{!?with_static_libs:--disable-static} \
	%{!?with_sse:--disable-x86-asm}
%{__make}

%if %{with doc}
%{__make} -C doc html
%endif

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

%{__rm}	$RPM_BUILD_ROOT%{py3_sitedir}/vapoursynth.la
# obsoleted by pkg-config
%{__rm} $RPM_BUILD_ROOT%{_libdir}/libvapoursynth*.la
# dlopened modules
%{__rm} $RPM_BUILD_ROOT%{_libdir}/vapoursynth/*.la

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc ChangeLog ofl.txt
%attr(755,root,root) %{_bindir}/vspipe
%attr(755,root,root) %{_libdir}/libvapoursynth.so
%attr(755,root,root) %{_libdir}/libvapoursynth-script.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libvapoursynth-script.so.0
%attr(755,root,root) %{py3_sitedir}/vapoursynth.so
%dir %{_libdir}/vapoursynth
%attr(755,root,root) %{_libdir}/vapoursynth/libeedi3.so
%attr(755,root,root) %{_libdir}/vapoursynth/libmiscfilters.so
%attr(755,root,root) %{_libdir}/vapoursynth/libmorpho.so
%attr(755,root,root) %{_libdir}/vapoursynth/libremovegrain.so
%attr(755,root,root) %{_libdir}/vapoursynth/libvinverse.so
%attr(755,root,root) %{_libdir}/vapoursynth/libvivtc.so

%files plugin-imwri
%defattr(644,root,root,755)
# R: ImageMagick-c++ >= 1:7
%attr(755,root,root) %{_libdir}/vapoursynth/libimwri.so

%files plugin-ocr
%defattr(644,root,root,755)
# R: tesseract
%attr(755,root,root) %{_libdir}/vapoursynth/libocr.so

%if %{with ffmpeg}
%files plugin-subtext
%defattr(644,root,root,755)
# R: libass ffmpeg
%attr(755,root,root) %{_libdir}/vapoursynth/libsubtext.so
%endif

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
%doc doc/_build/html/{_static,api,functions,plugins,*.html,*.js}
%endif
