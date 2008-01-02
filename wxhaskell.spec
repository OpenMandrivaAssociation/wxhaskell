%define name wxhaskell
%define ver 0.9.4-1
%define rel 2

%define ghc_version %(rpm -q ghc | cut -d- -f2)

%define version %(echo %{ver} | sed -e 's/-/./g')
%define sVersion %(echo %{ver} | cut -d- -f1)

%define libname %mklibname %name

Summary:	wxWindows Haskell binding
Name:		%name
Version:	%version
Release: 	%mkrel %rel
License:	LGPLish
Group: 		Development/Other
URL: 		http://wxhaskell.sourceforge.net
Source0: 	http://ovh.dl.sourceforge.net/sourceforge/%name/%name-src-%{ver}.tar.bz2
Patch0: 	wxhaskell-permissive-PIC.patch
BuildRequires: 	ghc == %ghc_version
BuildRequires: 	libwxgtk2.6-devel
BuildRequires: 	haddock >= 0.7
BuildRoot: 	%{_tmppath}/%{name}-%{version}-%{release}-root


%description
wxHaskell is a Haskell binding to the portable wxWidgets GUI library.

%package -n ghc-%name
Summary:        Haskell binding for wxGTK2 devel files
Group:          Development/Other
Requires:	ghc == %ghc_version
Requires:	%libname == %version
# for ghc-pkg
Requires(pre): 	ghc == %ghc_version
Requires(post): ghc == %ghc_version

%description -n ghc-%name
wxHaskell is a Haskell binding to the portable wxWidgets GUI library.

This package contains the wxhaskell package for ghc.

%package -n %libname
Summary:        Haskell binding for wxGTK2 devel files
Group:          Development/Other
Provides:	%name == %version

%description -n %libname
wxHaskell is a Haskell binding to the portable wxWidgets GUI library.


%package doc
Summary: 	Haskell binding for wxGTK2 documentation
Group: 		Development/Other

%description doc
wxHaskell is a Haskell binding to the portable wxWidgets GUI library.

This package contains the documentation in html format.


%define wxdir %{_libdir}/ghc-%{ghc_version}/wx

%prep
%setup -q -n wxhaskell-%sVersion
# %ifarch x86_64
%patch0
# %endif

%build
./configure --hc=ghc-%{ghc_version} --hcpkg=ghc-pkg-%{ghc_version} --libdir=%{wxdir} --with-opengl --wx-config=wx-config-ansi
# build fails with %make on a multiproc system
make all
%make doc

%install
rm -rf $RPM_BUILD_ROOT
make install-files LIBDIR=%buildroot%{wxdir}
cp -p config/wx.pkg %buildroot%{wxdir}
cp -p config/wxcore.pkg %buildroot%{wxdir}
sed -i -e "s|\${wxhlibdir}|%{wxdir}|" %buildroot%{wxdir}/wx*.pkg

# move wrapper lib to libdir since no rpath in package config
mv %buildroot%{wxdir}/libwxc-*.so %buildroot%{_libdir}

# remove object files and generated them at pkg install time
rm %buildroot%{wxdir}/wx*.o

%clean
rm -rf $RPM_BUILD_ROOT

%post -n %libname -p /sbin/ldconfig

%postun -n %libname -p /sbin/ldconfig

%post -n ghc-%name
/sbin/ldconfig
ghc-pkg-%{ghc_version} update -g %{wxdir}/wxcore.pkg
ghc-pkg-%{ghc_version} update -g %{wxdir}/wx.pkg

%preun -n ghc-%name
if [ "$1" = 0 ]; then
  rm %{wxdir}/wx*.o
  ghc-pkg-%{ghc_version} unregister wx || :
  ghc-pkg-%{ghc_version} unregister wxcore || :
fi
/sbin/ldconfig

%files -n %libname
%defattr(-,root,root,-)
%{_libdir}/libwxc-*.so
%doc *.txt

%files -n ghc-%name
%defattr(-,root,root,-)
%{wxdir}/*

%files doc
%defattr(-,root,root,-)
%doc out/doc/* samples

