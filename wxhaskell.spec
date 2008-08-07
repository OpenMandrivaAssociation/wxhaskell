# The wxhaskell build process has to be split into two steps these
# days, so the previous wxhaslell .src.rpm is now split into two:
# wxhaskell and wxhaskell-wx . It would be better to have
# wxhaskell-core and wxhaskell , but this keeps history better.
# wxhaskell builds the wxcore part. wxhaskell-wx builds the wx part.
# The wx build can't succeed unless the wxcore part has already been
# installed, hence the need for two source packages. -AdamW 2008/08

%define ghc_version %(rpm -q ghc | cut -d- -f2)
%define libname %mklibname %name

Summary:	wxWindows Haskell binding
Name:		wxhaskell
Version:	0.10.3
Release: 	%{mkrel 2}
License:	wxWidgets
Group: 		Development/Other
URL: 		http://wxhaskell.sourceforge.net
Source0: 	http://downloads.sourgeforge.net/%{name}/%{name}-src-%{version}.zip
# Disable the API documentation build - it doesn't work due to haddock
# problems (boy, I never thought I'd write THAT) - AdamW 2008/08
Patch0:		wxhaskell-0.10.3-disableapidocs.patch
BuildRequires:	ghc
BuildRequires:	wxgtku2.6-devel
BuildRequires:	haddock >= 0.7
#BuildRequires:	haskell-macros
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root

%description
wxHaskell is a Haskell binding to the portable wxWidgets GUI library.

%package -n haskell-wxcore
Summary:	Haskell binding for wxGTK2 devel files
Group:		Development/Other
Requires:	ghc == %{ghc_version}
Requires:	%{libname} == %{version}
Conflicts:	ghc-%{name} < %{version}-%{release}
Obsoletes:	ghc-%{name}-core < %{version}-%{release}
Provides:	ghc-%{name}-core = %{version}-%{release}
# for ghc-pkg
Requires(pre):	ghc == %{ghc_version}
Requires(post):	ghc == %{ghc_version}

%description -n haskell-wxcore
wxHaskell is a Haskell binding to the portable wxWidgets GUI library.
This package contains the wxhaskell package for ghc.

%package -n %{libname}
Summary:	Haskell binding for wxGTK2 devel files
Group:		Development/Other
Provides:	%{name} == %{version}

%description -n %{libname}
wxHaskell is a Haskell binding to the portable wxWidgets GUI library.

%package doc
Summary:	Haskell binding for wxGTK2 documentation
Group:		Development/Other

%description doc
wxHaskell is a Haskell binding to the portable wxWidgets GUI library.
This package contains the documentation in html format.

%define wxdir %{_libdir}/ghc-%{ghc_version}/wx

%prep
%setup -q
%patch0 -p1 -b .apidoc

%build
./configure --hc=ghc-%{ghc_version} --hcpkg=ghc-pkg-%{ghc_version} --libdir=%{wxdir} --with-opengl --wx-config=wx-config-unicode
# build fails with %make on a multiproc system
make
make doc

%install
rm -rf %{buildroot}
make wxcore-install-files LIBDIR=%{buildroot}%{wxdir}
cp -p config/wxcore.pkg %{buildroot}%{wxdir}
sed -i -e "s|\${wxhlibdir}|%{wxdir}|" %{buildroot}%{wxdir}/wxcore.pkg

# move wrapper lib to libdir since no rpath in package config
mv %{buildroot}%{wxdir}/libwxc-*.so %{buildroot}%{_libdir}

# remove object files and generated them at pkg install time
rm %{buildroot}%{wxdir}/wx*.o

# remove wx first as we're not building it here
#rm -rf wx
#{_cabal_rpm_gen_deps}

%clean
rm -rf %{buildroot}

%if %mdkversion < 200900
%post -n %{libname} -p /sbin/ldconfig
%endif

%if %mdkversion < 200900
%postun -n %{libname} -p /sbin/ldconfig
%endif

%post -n haskell-wxcore
%if %mdkversion < 200900
/sbin/ldconfig
%endif
ghc-pkg-%{ghc_version} update -g %{wxdir}/wxcore.pkg

%preun -n haskell-wxcore
if [ "$1" = 0 ]; then
  rm %{wxdir}/wx*.o
  ghc-pkg-%{ghc_version} unregister wxcore || :
fi

%if %mdkversion < 200900
%postun -n haskell-wxcore -p /sbin/ldconfig
%endif

%files -n %{libname}
%defattr(-,root,root,-)
%{_libdir}/libwxc-*.so
%doc *.txt

%files -n haskell-wxcore
%defattr(-,root,root,-)
%{wxdir}
#_cabal_rpm_files

%files doc
%defattr(-,root,root,-)
%doc dist/doc/html/* samples

