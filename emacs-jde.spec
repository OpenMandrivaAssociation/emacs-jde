%define gcj_support     1

%define fname           jde
%define elibdir         %{_datadir}/emacs/site-lisp/elib
%define cedetdir        %{_datadir}/emacs/site-lisp/cedet
%define jdedir          %{_datadir}/emacs/site-lisp/jde

Name:           emacs-%{fname}
Version:        2.3.5.1
Release:        %mkrel 9
Epoch:          0
Summary:        The Java Development Environment for Emacs (JDEE)
Requires:       emacs >= 0:20.7
License:        GPL
URL:            http://jdee.sunsite.dk/
Source0:        http://jdee.sunsite.dk/jde-latest.tar.bz2
Patch0:         %{name}-build.patch
Group:          Development/Java
Obsoletes:      jde
Provides:       jde = %{epoch}:%{version}-%{release}
%if %{gcj_support}
BuildRequires:  java-gcj-compat-devel
%else
BuildArch:      noarch
%endif
Requires:       ant
Requires:       bsh
Requires:       checkstyle
Requires:       emacs-bin
Requires:       emacs-cedet
Requires:       emacs-elib
Requires:       java
Requires:       junit
BuildRequires:  emacs-bin
BuildRequires:  emacs-cedet
BuildRequires:  emacs-elib
BuildRequires:  java-devel
BuildRequires:  java-rpmbuild
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root

%description
The Java Development Environment for Emacs (JDEE) is an Emacs Lisp
package that interfaces Emacs to third-party Java application
development tools, such as those provided by JavaSoft's Java Development
Kit (JDK). The result is an integrated development environment (IDE)
comparable in power to many commercial Java IDEs.

%prep
%setup -q -n %{fname}-%{version}
%patch0 -p1
find . -type f -name "*.jar" | xargs %{__rm} -f
find . -type f -name ".nosearch" | xargs %{__rm} -f
%{__perl} -pi -e 's|defconst jde-cedet-min-version.*|defconst jde-cedet-min-version "1.0pre3"|;' \
              -e 's|"beta"|"pre"|g' lisp/jde.el

%build
(cd lisp && %{__make} \
        ELIB=%{elibdir} \
        CEDET=%{cedetdir})

%{__rm} -rf java/src/jde/debugger
(cd java/src && %{javac} -source 1.4 -target 1.4 -d ../classes `find . -type f -name \*.java`)
(cd java/classes && %{jar} cf ../lib/jde.jar `find . -type f -name \*.class`)
%{__rm} -rf java/classes

%install
%{__rm} -rf %{buildroot}
%{__mkdir_p} %{buildroot}%{_datadir}/emacs/site-lisp/%{fname}
%{__mkdir_p} %{buildroot}%{jdedir}

%{__cp} -a doc %{buildroot}%{jdedir}
%{__cp} -a java %{buildroot}%{jdedir}
%{__mkdir_p} %{buildroot}%{jdedir}/lisp
%{__cp} -a lisp/*.el %{buildroot}%{jdedir}/lisp
%{__mv} lisp/ChangeLog lisp/ReleaseNotes.txt .

%{__mkdir_p} %{buildroot}%{_sysconfdir}/emacs/site-start.d
%{__cat} > %{buildroot}%{_sysconfdir}/emacs/site-start.d/%{fname}.el << EOF
(add-to-list 'load-path (expand-file-name "%{jdedir}/lisp"))
(add-to-list 'load-path (expand-file-name "%{elibdir}"))
(require 'jde)
(autoload 'jde-mode "jde" "Java Development Environment" t)
(add-to-list 'auto-mode-alist '("\\.java$" . jde-mode))
EOF

%{__mkdir_p} %{buildroot}%{_javadir}
%{__install} -m 644 java/lib/jde.jar %{buildroot}%{_javadir}/jde-%{version}.jar
%{__rm} -f %{buildroot}%{jdedir}/java/lib/jde.jar
(cd %{buildroot}%{_javadir} && %{__ln_s} jde-%{version}.jar jde.jar)

pushd %{buildroot}%{jdedir}/java/lib
%{__rm} -f LICENSE.* RIGHTS.*
%{__ln_s} %{_javadir}/bsh.jar bsh.jar
%{__ln_s} %{_javadir}/checkstyle.jar checkstyle-all.jar
%{__rm} -f sun_checks.xml
%{__ln_s} %{_docdir}/checkstyle-4.?/sun_checks.xml sun_checks.xml
%{__ln_s} %{_javadir}/jde.jar jde.jar
%{__ln_s} %{_javadir}/junit.jar junit.jar
popd

%{gcj_compile}

%{__perl} -pi -e 's|\r$||g' doc/tli_rbl/txt/jdebug-ug-toc.txt

%clean
%{__rm} -rf %{buildroot}

%if %{gcj_support}
%post
%{update_gcjdb}

%postun
%{clean_gcjdb}
%endif

%files
%defattr(0644,root,root,0755)
%config(noreplace) %{_sysconfdir}/emacs/site-start.d/%{fname}.el
%doc ChangeLog ReleaseNotes.txt
%{jdedir}
%{_javadir}/*.jar
%{gcj_files}
