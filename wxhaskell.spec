# The wxhaskell build process has to be split into two steps these
# days, so the previous wxhaskell .src.rpm is now split into two:
# wxhaskell and wxhaskell-wx . It would be better to have
# wxhaskell-core and wxhaskell , but this keeps history better.
# wxhaskell builds the wxcore part. wxhaskell-wx builds the wx part.
# The wx build can't succeed unless the wxcore part has already been
# installed, hence the need for two source packages. -AdamW 2008/08

%define ghc_version %(rpm -q ghc | cut -d- -f2)
%define libname %mklibname %name

%define rel	1
%define darcs	20090214
%if %darcs
%define release		%mkrel 0.%{darcs}.%{rel}
%define distname	%{name}-%{darcs}.tar.lzma
%define dirname		%{name}
%else
%define release		%mkrel %{rel}
%define distname	%{name}-src-%{version}.zip
%define dirname		%{name}-%{version}
%endif

Summary:	wxWindows Haskell binding
Name:		wxhaskell
Version:	0.12.1.6
Release: 	%{release}
License:	wxWidgets
Group: 		Development/Other
URL: 		http://wxhaskell.sourceforge.net
Source0: 	http://downloads.sourgeforge.net/%{name}/%{distname}
BuildRequires:	ghc
BuildRequires:	wxgtku-devel
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
%setup -q -n %{dirname}

%build
%if %darcs
chmod 0755 configure
%endif
./configure --hc=ghc-%{ghc_version} --hcpkg=ghc-pkg-%{ghc_version} --libdir=%{wxdir} --with-opengl --wx-config=wx-config-unicode
# build fails with %make on a multiproc system
make
#make doc

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
%doc samples
# dist/doc/html/* 



%changelog
* Wed Mar 16 2011 Stéphane Téletchéa <steletch@mandriva.org> 0.12.1.6-0.20090214.1mdv2011.0
+ Revision: 645490
- update to new version 0.12.1.6

* Sun Sep 20 2009 Thierry Vignaud <tv@mandriva.org> 0.11.1-0.20090214.2mdv2010.0
+ Revision: 445827
- rebuild

* Sun Feb 15 2009 Adam Williamson <awilliamson@mandriva.org> 0.11.1-0.20090214.1mdv2009.1
+ Revision: 340452
- drop disableapidocs.patch and just disable doc build entirely (doesn't work
  due to a ghc problem now)
- build against wxgtk 2.8 unicode
- bump to latest darcs (fixes problems with wxgtk 2.8)
- add conditionals for darcs build

* Fri Aug 08 2008 Adam Williamson <awilliamson@mandriva.org> 0.10.3-2mdv2009.0
+ Revision: 267492
- add use of haskell dep macro, but commented out as it doesn't currently work
- rename main package haskell-wxcore to comply with haskell policy

* Fri Aug 08 2008 Adam Williamson <awilliamson@mandriva.org> 0.10.3-1mdv2009.0
+ Revision: 267420
- rebuild for new era
- correct doc location
- own wxdir to stop it being orphaned on package removal
- don't do all the post-install stuff for wx, only wxcore (due to split)
- update the make commands
- correct the configure command for unicode wxgtk
- add conflict to ensure smooth upgrade
- rename main package to ghc-wxhaskell-core to reflect package split
- drop permissive-PIC.patch (no longer necessary)
- add disableapidocs.patch (disable API doc build, it doesn't work)
- br unicode wxgtk
- don't version the ghc buildrequire (won't work on a clean buildroot)
- correct license
- add comment explaining package split
- drop unnecessary defines
- new release 0.10.3

  + Pixel <pixel@mandriva.com>
    - do not call ldconfig in %%post/%%postun, it is now handled by filetriggers
    - ldconfig must be done in %%postun, not %%preun

  + Olivier Blin <oblin@mandriva.com>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request


* Mon May 15 2006 Gaetan Lehmann <gaetan.lehmann@jouy.inra.fr> 0.9.4.1-2mdk
- rebuild for new ghc

* Thu Oct 20 2005 Gaetan Lehmann <gaetan.lehmann@jouy.inra.fr> 0.9.4.1-1mdk
- 9.4-1
- initial mandrake contrib
- Patch0: fix build on x86_64
- split in more packages

* Mon Feb 28 2005 Jens Petersen <petersen@redhat.com> - 0.9-1
- build with opengl
- use ghcver
- build with CXX wrapper PIC on x86_64
  - add wxhaskell-0.9-cxx-PIC-x86_64.patch
- install with install-files target
  - wxhaskell-0.2-ghc-pkg.patch no longer needed
- move samples to doc subpackage
- install libwxc so in libdir to help package config
- remove object files from package and generate them at package install time
- install pkg config files in wxdir

* Thu Mar 25 2004 Jens Petersen <petersen@redhat.com> - 0.6-2
- update to 0.6
- build with ghc-6.2.1
- update summaries, groups and descriptions
- buildrequire haddock and build the documentation
- add -doc subpackage
- buildrequire wxGTK2-gl

* Fri Sep 19 2003 Jens Petersen <petersen@haskell.org> - 0.2-2
- install under ghc-%%{ghc_version}/wxhaskell, except libwxc.so
- post and preun scripts
- add some docs

* Fri Sep 19 2003 Jens Petersen <petersen@haskell.org> - 0.2-1
- Initial build.

