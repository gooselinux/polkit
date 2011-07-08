Summary: PolicyKit Authorization Framework
Name: polkit
Version: 0.96
Release: 2%{?dist}
License: LGPLv2+
URL: http://www.freedesktop.org/wiki/Software/PolicyKit
Source0: http://hal.freedesktop.org/releases/%{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
Group: System Environment/Libraries
BuildRequires: glib2-devel
BuildRequires: expat-devel
BuildRequires: pam-devel
BuildRequires: eggdbus-devel
BuildRequires: gtk-doc
BuildRequires: intltool

Requires: ConsoleKit
Requires: dbus

Obsoletes: PolicyKit <= 0.10
Provides: PolicyKit = 0.11

%description
PolicyKit is a toolkit for defining and handling authorizations.
It is used for allowing unprivileged processes to speak to privileged
processes.

%package devel
Summary: Development files for PolicyKit
Group: Development/Libraries
Requires: %name = %{version}-%{release}
Requires: %name-docs = %{version}-%{release}
Requires: pkgconfig
Requires: glib2-devel
Obsoletes: PolicyKit-devel <= 0.10
Provides: PolicyKit-devel = 0.11

%description devel
Development files for PolicyKit.

%package docs
Summary: Development documentation for PolicyKit
Group: Development/Libraries
Requires: %name-devel = %{version}-%{release}
Requires: gtk-doc
Obsoletes: PolicyKit-docs <= 0.10
Provides: PolicyKit-docs = 0.11

%description docs
Development documentation for PolicyKit.

%package desktop-policy
Summary: Roles and default policy for desktop usage
Group: Development/Libraries
#Requires: %name = %{version}-%{release}
Requires(pre): /usr/sbin/groupadd
Requires(preun): /usr/sbin/groupdel
BuildArch: noarch

%description desktop-policy
Roles and default policy for desktop usage.

%prep
%setup -q

%build
%configure --enable-gtk-doc --disable-static --libexecdir=%{_libexecdir}/polkit-1 --enable-examples --disable-introspection
make

%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT

rm -f $RPM_BUILD_ROOT%{_libdir}/*.la
rm -f $RPM_BUILD_ROOT%{_libdir}/polkit-1/extensions/*.la

# fix up multilib problems in the docs
sed -i -e "s#/usr/lib/polkit-1/extensions#\${libdir}/polkit-1/extensions#" \
       -e "s#/usr/lib64/polkit-1/extensions#\${libdir}/polkit-1/extensions#" \
      $RPM_BUILD_ROOT%{_datadir}/gtk-doc/html/polkit-1/polkit-extending.html
sed -i -e "s#/usr/lib/polkit-1/extensions#\${libdir}/polkit-1/extensions#" \
       -e "s#/usr/lib64/polkit-1/extensions#\${libdir}/polkit-1/extensions#" \
      $RPM_BUILD_ROOT%{_datadir}/gtk-doc/html/polkit-1/polkit-1-polkitunixprocess.html

%find_lang polkit-1

###
### BEGIN DESKTOP POLICY CONFIGURATION ###
###

cat > $RPM_BUILD_ROOT%{_sysconfdir}/polkit-1/localauthority.conf.d/60-desktop-policy.conf << EOF
# This allows users in the desktop_admin_r group to authenticate as
# the administrator.
#
# DO NOT EDIT THIS FILE, it will be overwritten on update.

[Configuration]
AdminIdentities=unix-group:desktop_admin_r
EOF

cat > $RPM_BUILD_ROOT%{_localstatedir}/lib/polkit-1/localauthority/10-vendor.d/10-desktop-policy.pkla << EOF
# Authorizations/policy for the desktop_admin_r and desktop_user_r groups.
#
# DO NOT EDIT THIS FILE, it will be overwritten on update.

# Allow "standard users" to do some things without being interrupted by
# password dialogs (TODO: not complete)
#
[Desktop User Permissions]
Identity=unix-group:desktop_user_r
Action=org.gnome.clockapplet.mechanism.settimezone
ResultAny=no
ResultInactive=no
ResultActive=yes

# Allow "administrative users" to do a lot of things without being interrupted by
# password dialogs (TODO: not complete)
#
[Desktop Administrator Permissions]
Identity=unix-group:desktop_admin_r
Action=org.gnome.clockapplet.mechanism.*;org.freedesktop.udisks.*;org.freedesktop.RealtimeKit1.*
ResultAny=no
ResultInactive=no
ResultActive=yes

EOF

###
### END DESKTOP POLICY CONFIGURATION
###

%clean
rm -rf $RPM_BUILD_ROOT

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%pre desktop-policy
/usr/sbin/groupadd -r desktop_admin_r 2> /dev/null || :
/usr/sbin/groupadd -r desktop_user_r 2> /dev/null || :

%files desktop-policy
%{_sysconfdir}/polkit-1/localauthority.conf.d/60-desktop-policy.conf
%{_localstatedir}/lib/polkit-1/localauthority/10-vendor.d/10-desktop-policy.pkla

%files -f polkit-1.lang
%defattr(-,root,root,-)
%doc COPYING
%{_libdir}/lib*.so.*
%dir %{_libdir}/polkit-1
%dir %{_libdir}/polkit-1/extensions
%{_libdir}/polkit-1/extensions/*.so
%{_datadir}/man/man1/*
%{_datadir}/man/man8/*
%{_datadir}/dbus-1/system-services/*
%dir %{_datadir}/polkit-1/
%dir %{_datadir}/polkit-1/actions
%{_datadir}/polkit-1/actions/org.freedesktop.policykit.policy
%{_sysconfdir}/dbus-1/system.d/org.freedesktop.PolicyKit1.conf
%{_sysconfdir}/pam.d/polkit-1
%{_sysconfdir}/polkit-1
%{_bindir}/pkaction
%{_bindir}/pkcheck
%{_libexecdir}/polkit-1/polkitd

# see upstream docs for why these permissions are necessary
%attr(4755,root,root) %{_bindir}/pkexec
%attr(4755,root,root) %{_libexecdir}/polkit-1/polkit-agent-helper-1

%attr(0700,root,root) %dir %{_localstatedir}/lib/polkit-1/
%dir %{_localstatedir}/lib/polkit-1/localauthority
%dir %{_localstatedir}/lib/polkit-1/localauthority/10-vendor.d
%dir %{_localstatedir}/lib/polkit-1/localauthority/20-org.d
%dir %{_localstatedir}/lib/polkit-1/localauthority/30-site.d
%dir %{_localstatedir}/lib/polkit-1/localauthority/50-local.d
%dir %{_localstatedir}/lib/polkit-1/localauthority/90-mandatory.d

%files devel
%defattr(-,root,root,-)
%{_libdir}/lib*.so
%{_libdir}/pkgconfig/*.pc
%{_includedir}/*
%{_bindir}/pk-example-frobnicate
%{_datadir}/polkit-1/actions/org.freedesktop.policykit.examples.pkexec.policy

%files docs
%defattr(-,root,root,-)
%{_datadir}/gtk-doc/html/*

%changelog
* Mon Jun 21 2010 Matthias Clasen <mclasen@redhat.com> - 0.96-2
- Fix a multilib problem
Resolves: #605099

* Fri Jan 15 2010 David Zeuthen <davidz@redhat.com> - 0.96-1
- Update to 0.96
- Related: rhbz#543948

* Wed Jan 13 2010 David Zeuthen <davidz@redhat.com> - 0.95-4
- Rebuild
- Related: rhbz#543948

* Wed Jan 13 2010 David Zeuthen <davidz@redhat.com> - 0.95-3
- Disable GObject Introspection
- Related: rhbz#543948

* Fri Nov 13 2009 David Zeuthen <davidz@redhat.com> - 0.95-2
- Rebuild

* Fri Nov 13 2009 David Zeuthen <davidz@redhat.com> - 0.95-1
- Update to 0.95
- Drop upstreamed patches

* Tue Oct 20 2009 Matthias Clasen <mclasen@redhat.com> - 0.95-0.git20090913.3
- Fix a typo in pklocalauthority(8)

* Mon Sep 14 2009 David Zeuthen <davidz@redhat.com> - 0.95-0.git20090913.2
- Refine how Obsolete: is used and also add Provides: (thanks Jesse
  Keating and nim-nim)

* Mon Sep 14 2009 David Zeuthen <davidz@redhat.com> - 0.95-0.git20090913.1
- Add bugfix for polkit_unix_process_new_full() (thanks Bastien Nocera)
- Obsolete old PolicyKit packages

* Sun Sep 13 2009 David Zeuthen <davidz@redhat.com> - 0.95-0.git20090913
- Update to git snapshot
- Drop upstreamed patches
- Turn on GObject introspection
- Don't delete desktop_admin_r and desktop_user_r groups when
  uninstalling polkit-desktop-policy

* Fri Sep 11 2009 David Zeuthen <davidz@redhat.com> - 0.94-4
- Add some patches from git master
- Sort pkaction(1) output
- Bug 23867 – UnixProcess vs. SystemBusName aliasing

* Thu Aug 13 2009 David Zeuthen <davidz@redhat.com> - 0.94-3
- Add desktop_admin_r and desktop_user_r groups along with a first cut
  of default authorizations for users in these groups.

* Wed Aug 12 2009 David Zeuthen <davidz@redhat.com> - 0.94-2
- Disable GObject Introspection for now as it breaks the build

* Wed Aug 12 2009 David Zeuthen <davidz@redhat.com> - 0.94-1
- Update to upstream release 0.94

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.93-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Mon Jul 20 2009 David Zeuthen <davidz@redhat.com> - 0.93-2
- Rebuild

* Mon Jul 20 2009 David Zeuthen <davidz@redhat.com> - 0.93-1
- Update to 0.93

* Tue Jun 09 2009 David Zeuthen <davidz@redhat.com> - 0.92-3
- Don't make docs noarch (I *heart* multilib)
- Change license to LGPLv2+

* Mon Jun 08 2009 David Zeuthen <davidz@redhat.com> - 0.92-2
- Rebuild

* Mon Jun 08 2009 David Zeuthen <davidz@redhat.com> - 0.92-1
- Update to 0.92 release

* Wed May 27 2009 David Zeuthen <davidz@redhat.com> - 0.92-0.git20090527
- Update to 0.92 snapshot

* Mon Feb  9 2009 David Zeuthen <davidz@redhat.com> - 0.91-1
- Initial spec file.
