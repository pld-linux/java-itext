# OTOD
# - javadoc fetches from net:
#  [javadoc] Constructing Javadoc information...
#  [javadoc] javadoc: warning - Error fetching URL: http://www.dom4j.org/apidocs/package-list
#  [javadoc] javadoc: warning - Error fetching URL: https://pdf-renderer.dev.java.net/nonav/demos/latest/javadoc/package-list
#
# Conditional build:
%bcond_without	javadoc		# don't build javadoc

%define		srcname	iText
%define		pname	itext
%include	/usr/lib/rpm/macros.java
Summary:	A Free Java-PDF library
Name:		java-%{pname}
Version:	2.1.7
Release:	1
License:	(LGPLv2+ or MPLv1.1) and ASL 2.0 and BSD and LGPLv2+
Group:		Libraries/Java
URL:		http://www.lowagie.com/iText/
Source0:	http://downloads.sourceforge.net/itext/iText-src-%{version}.tar.gz
# Source0-md5:	38c3d47e0f0a87a8151b5b2f208b461e
Source3:	itext-rups.sh
Source4:	itext-rups.desktop
Source5:	itext-toolbox.sh
Source6:	itext-toolbox.desktop
Patch1:		pdftk.patch
# Maven's Doxia plugin explicitly requires these XML output interfaces
# of iText.  They were removed in iText 1.4.4 [1].  iText versions prior
# to 1.5.x had questionable licensing [2] so rather than try to create
# an itext1 package, I have forward-ported these classes.  The doxia
# developers have told me on IRC on 2009-08-27 that the iText dependency
# will likely be deprecated meaning we won't have to keep these forever.
#
# I've opened a bug with iText:
#
# https://sourceforge.net/tracker/?func=detail&aid=2846427&group_id=15255&atid=365255
#
# and commented on the Doxia but related to this:
#
# http://jira.codehaus.org/browse/DOXIA-53
#
# -- Andrew Overholt, 2009-08-28
#
# [1]
# http://www.1t3xt.com/about/history.php?branch=history.10&node=14
# [2]
# https://bugzilla.redhat.com/show_bug.cgi?id=236309
Patch3:		itext-xmloutput.patch
BuildRequires:	ImageMagick
BuildRequires:	ant
BuildRequires:	desktop-file-utils
BuildRequires:	java-bctsp
BuildRequires:	java-dom4j
BuildRequires:	java-pdf-renderer
BuildRequires:	jdk >= 1.6
BuildRequires:	jpackage-utils
BuildRequires:	rpm-javaprov
BuildRequires:	rpmbuild(macros) >= 1.553
%if %(locale -a | grep -q '^en_US$'; echo $?)
BuildRequires:	glibc-localedb-all
%endif
Requires:	java >= 1.5
Requires:	java-bctsp
Requires:	jpackage-utils >= 1.5
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
iText is a library that allows you to generate PDF files on the fly.
The iText classes are very useful for people who need to generate
read-only, platform independent documents containing text, lists,
tables and images. The library is especially useful in combination
with Java(TM) technology-based Servlets: The look and feel of HTML is
browser dependent; with iText and PDF you can control exactly how your
servlet's output will look.

%package rtf
Summary:	Library to output Rich Text Files
License:	MPLv1.1 or LGPLv2+
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description rtf
The RTF package is an extension of the iText library and allows iText
to output Rich Text Files in additon to PDF files. These files can
then be viewed and edited with RTF viewers such as OpenOffice.org
Writer.

%package rups
Summary:	Reading/Updating PDF Syntax
License:	LGPLv2+ and CC-BY
Group:		X11/Applications
Requires:	%{name} = %{version}-%{release}
Requires:	gtk-update-icon-cache
Requires:	java-dom4j
Requires:	java-pdf-renderer

%description rups
iText RUPS is a tool that combines SUN's PDF Renderer (to view PDF
documents), iText's PdfReader (to inspect the internal structure of a
PDF file), and iText's PdfStamper to manipulate a PDF file.

%package toolbox
Summary:	Some iText tools
License:	MPLv1.1 or MIT
Group:		X11/Applications
Requires:	%{name} = %{version}-%{release}
Requires:	gtk-update-icon-cache

%description toolbox
iText is a free open source Java-PDF library released on SF under the
MPL/LGPL; iText comes with a simple GUI: the iText toolbox. The
original developers of iText want to publish this toolbox as a
separate project under the more permissive MIT license. This is a
utility that allows you to use a number of iText tools.

%package javadoc
Summary:	Javadoc for iText
Group:		Documentation
Requires:	%{name} = %{version}-%{release}
Requires:	jpackage-utils

%description javadoc
API documentation for the iText package.

%prep
%setup -qcT -a 0
%patch1 -p1
%patch3 -p0

# Remove preshipped binaries
find -name "*.jar" | xargs -r rm -v

# Fix encoding issues
%undos src/rups/com/lowagie/rups/view/icons/copyright_notice.txt

install -d lib
# Remove jdk & version numbers from classpath entries
for file in src/ant/{*,.ant*}; do
	for jarname in bcmail bcprov bctsp dom4j; do
		sed -i "s|$jarname-.*\.jar|$jarname.jar|" $file
	done
done

# Remove classpath elements from manifest
sed -i '\|Class-Path|d' src/ant/compile.xml

# Setting debug="on" on javac part of the build script.
sed -i 's|destdir|debug="on" destdir|g' src/ant/compile.xml
sed -i 's|debug="true"||g' src/ant/compile.xml

%build
# source code not US-ASCII
export LC_ALL=en_US

build-jar-repository -s -p lib bcprov bcmail bctsp pdf-renderer dom4j

CLASSPATH=$(build-classpath bcprov bcmail bctsp pdf-renderer dom4j)
cd src
%ant jar jar.rups jar.rtf jar.toolbox %{?with_javadoc:javadoc}

%install
rm -rf $RPM_BUILD_ROOT

# jars
install -d $RPM_BUILD_ROOT%{_javadir}
cp -p lib/iText.jar $RPM_BUILD_ROOT%{_javadir}/%{srcname}-%{version}.jar
ln -s %{srcname}-%{version}.jar $RPM_BUILD_ROOT%{_javadir}/%{srcname}.jar
cp -p lib/iText-rtf.jar $RPM_BUILD_ROOT%{_javadir}/%{srcname}-rtf-%{version}.jar
ln -s %{srcname}-rtf-%{version}.jar $RPM_BUILD_ROOT%{_javadir}/%{srcname}-rtf.jar
cp -p lib/iText-rups.jar $RPM_BUILD_ROOT%{_javadir}/%{srcname}-rups-%{version}.jar
ln -s %{srcname}-rups-%{version}.jar $RPM_BUILD_ROOT%{_javadir}/%{srcname}-rups.jar
cp -p lib/iText-toolbox.jar $RPM_BUILD_ROOT%{_javadir}/%{srcname}-toolbox-%{version}.jar
ln -s %{srcname}-toolbox-%{version}.jar $RPM_BUILD_ROOT%{_javadir}/%{srcname}-toolbox.jar

install -d $RPM_BUILD_ROOT{%{_bindir},%{_desktopdir}}
# rups stuff
install -p %{SOURCE3} $RPM_BUILD_ROOT%{_bindir}/%{pname}-rups
desktop-file-install \
      --dir=${RPM_BUILD_ROOT}%{_desktopdir} \
      %{SOURCE4}

# toolbox stuff
install -p %{SOURCE5} $RPM_BUILD_ROOT%{_bindir}/%{pname}-toolbox
desktop-file-install \
      --dir=${RPM_BUILD_ROOT}%{_desktopdir} \
      %{SOURCE6}

# icon for rups and toolbox
install -d $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/128x128/apps
convert -resize 128x128 src/toolbox/com/lowagie/toolbox/1t3xt.gif %{pname}.png
cp -p %{pname}.png $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/128x128/apps/%{pname}-rups.png
cp -p %{pname}.png $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/128x128/apps/%{pname}-toolbox.png

# javadoc
%if %{with javadoc}
install -d $RPM_BUILD_ROOT%{_javadocdir}/%{srcname}-%{version}
cp -a build/docs/* $RPM_BUILD_ROOT%{_javadocdir}/%{srcname}-%{version}
ln -s %{srcname}-%{version} $RPM_BUILD_ROOT%{_javadocdir}/%{srcname} # ghost symlink
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post rups
%update_icon_cache hicolor

%postun rups
%update_icon_cache hicolor

%post toolbox
%update_icon_cache hicolor

%postun toolbox
%update_icon_cache hicolor

%post javadoc
ln -nfs %{srcname}-%{version} %{_javadocdir}/%{srcname}

%files
%defattr(644,root,root,755)
%doc build/bin/com/lowagie/text/{apache_license,lgpl,misc_licenses,MPL-1.1}.txt
%{_javadir}/%{srcname}.jar
%{_javadir}/%{srcname}-%{version}.jar

%files rtf
%defattr(644,root,root,755)
%{_javadir}/%{srcname}-rtf.jar
%{_javadir}/%{srcname}-rtf-%{version}.jar

%files rups
%defattr(644,root,root,755)
%doc src/rups/com/lowagie/rups/view/icons/copyright_notice.txt
%{_javadir}/%{srcname}-rups.jar
%{_javadir}/%{srcname}-rups-%{version}.jar
%attr(755,root,root) %{_bindir}/%{pname}-rups
%{_desktopdir}/%{pname}-rups.desktop
%{_iconsdir}/hicolor/128x128/apps/%{pname}-rups.png

%files toolbox
%defattr(644,root,root,755)
%doc src/toolbox/com/lowagie/toolbox/tools.txt
%{_javadir}/%{srcname}-toolbox.jar
%{_javadir}/%{srcname}-toolbox-%{version}.jar
%attr(755,root,root) %{_bindir}/%{pname}-toolbox
%{_desktopdir}/%{pname}-toolbox.desktop
%{_iconsdir}/hicolor/128x128/apps/%{pname}-toolbox.png

%if %{with javadoc}
%files javadoc
%defattr(644,root,root,755)
%{_javadocdir}/%{srcname}-%{version}
%ghost %{_javadocdir}/%{srcname}
%endif
