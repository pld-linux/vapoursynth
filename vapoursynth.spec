#
# Conditional build:
%bcond_without	doc		# documentation
%bcond_without	static_libs	# static libraries
#
Summary:	A video processing framework with simplicity in mind
Summary(pl.UTF-8):	Szkielet do przetwarzania obrazu stworzony z myślą o prostocie
Name:		vapoursynth
# versions >= 73 removes VSScript v3 API, used by ffmpeg 6.1.x
# versions >= 77 (or lower) removes system-wide library, moving all to python plugin tree
Version:	81
Release:	0.2
License:	LGPL v2.1+
Group:		Libraries
#Source0Download: https://github.com/vapoursynth/vapoursynth/releases
Source0:	https://github.com/vapoursynth/vapoursynth/archive/R%{version}/%{name}-R%{version}.tar.gz
# Source0-md5:	1a60f95419daf7e6147ef5b68c688518
Patch0:		system-glslang.patch
URL:		http://www.vapoursynth.com/
BuildRequires:	Vulkan-Headers
BuildRequires:	glslang-devel >= 16.4.0
BuildRequires:	libstdc++-devel >= 6:7
%if %{with sse}
BuildRequires:	nasm
%endif
BuildRequires:	pkgconfig
BuildRequires:	python3-Cython >= 3.3.0
BuildRequires:	python3-devel >= 1:3.2
BuildRequires:	python3-meson-python >= 0.22.1
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
Obsoletes:	vapoursynth-static < 81

%description devel
Header files for VapourSynth libraries.

%description devel -l pl.UTF-8
Pliki nagłówkowe bibliotek VapourSynth.

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
%patch -P0 -p1

%build
export LDFLAGS="%{rpmldflags}"
%ifarch %{ix86}
export CFLAGS="%{rpmcflags} -msse2"
export CXXFLAGS="%{rpmcxxflags} -msse2"
%else
export CFLAGS="%{rpmcflags}"
export CXXFLAGS="%{rpmcxxflags}"
%endif
%py3_build_pyproject \
%ifarch %{x8664}
	-Csetup-args="-Denable_x86_asm=true" \
%else
	-Csetup-args="-Denable_x86_asm=false" \
%endif
	-Ccompile-args="--verbose" \
	-Ccompile-args="%{?_smp_mflags}"

%if %{with doc}
sphinx-build-3 -b html doc doc/_build/html
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_pkgconfigdir},{%{_libdir},%{_includedir}}/vapoursynth}

%py3_install_pyproject

ln -sr $RPM_BUILD_ROOT%{py3_sitedir}/vapoursynth/libvapoursynth.so.4 $RPM_BUILD_ROOT%{_libdir}
ln -sr $RPM_BUILD_ROOT%{py3_sitedir}/vapoursynth/libvapoursynth.so.4 $RPM_BUILD_ROOT%{_libdir}/libvapoursynth.so
ln -sr $RPM_BUILD_ROOT%{py3_sitedir}/vapoursynth/libvsscript.so $RPM_BUILD_ROOT%{_libdir}

%{__mv} $RPM_BUILD_ROOT%{py3_sitedir}/vapoursynth/include/* $RPM_BUILD_ROOT%{_includedir}/vapoursynth
%{__rm} -r $RPM_BUILD_ROOT%{py3_sitedir}/vapoursynth/include
%{__ln} -sr $RPM_BUILD_ROOT%{_includedir}/vapoursynth $RPM_BUILD_ROOT%{py3_sitedir}/vapoursynth/include

%{__rm} -r $RPM_BUILD_ROOT%{py3_sitedir}/vapoursynth/pkgconfig

# Installed pkgconfig is completely useless, wrong directories and no libs
cat >$RPM_BUILD_ROOT%{_pkgconfigdir}/vapoursynth.pc <<'EOF'
prefix=%{_prefix}
libdir=%{_libdir}
includedir=%{_includedir}/%{name}

Name: vapoursynth
Description: A frameserver for the 21st century
Version: %{version}
Cflags: -I${includedir}
Libs: -L${libdir} -lvapoursynth
EOF

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc ChangeLog README.md
%attr(755,root,root) %{_bindir}/vapoursynth
%attr(755,root,root) %{_bindir}/vspipe
%{_libdir}/libvapoursynth.so.4
%ghost %{_libdir}/libvsscript.so
%{py3_sitedir}/vapoursynth
%{py3_sitedir}/%{name}-%{version}.dist-info
%dir %{_libdir}/vapoursynth

%files devel
%defattr(644,root,root,755)
%{py3_sitedir}/vapoursynth/include
%{_libdir}/libvapoursynth.so
%{_includedir}/vapoursynth
%{_pkgconfigdir}/vapoursynth.pc

%if %{with doc}
%files doc
%defattr(644,root,root,755)
%doc doc/_build/html/{_static,functions,*.html,*.js}
%endif
