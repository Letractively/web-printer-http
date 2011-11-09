#!/usr/bin/perl

use CGI ':standard';
use Image::Magick;

@chars = ('a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','0','1','2','3','4','5','6','7','8','9');

use CGI;
$cgi = new CGI;

$printfile = $cgi->upload('print');


if ($printfile) {
print "Content-Type: text/html\n\nPrinting file...<br>";

$randomtext = "";

for ($i = 0; $i < 20; $i++) {
$randomtext = $randomtext . $chars[rand @chars];
}

open(TMP, ">/tmp/$randomtext");
flock(TMP,2);
binmode TMP;
while (<$printfile>) {
print TMP $_;
}
close(TMP);
chmod(0777,"/tmp/$randomtext");

open(PIPE, "/usr/bin/file /tmp/$randomtext --mime-type -b|");
$data = <PIPE>;
close(PIPE);

$data =~ s/\r//sgi;
$data =~ s/\t//sgi;
$data =~ s/\n//sgi;


($maintype, $subtype) = split("/", lc($data));

$res = "UNSUPPFORM";

if ($maintype eq "image") {
$image = Image::Magick->new;
$image->Read("/tmp/$randomtext");

open(TMP, ">/tmp/$randomtext");
flock(TMP,2);
$image->Write(file=>\*TMP, filename=>"/tmp/$randomtext.png");
close(TMP);
$image = undef;
system("lpr -r /tmp/$randomtext");
$res = "Image File";
}


if ($maintype eq "application") {
if ($subtype eq "pdf") {
system("lpr -r /tmp/$randomtext");
$res = "PDF File";
}
else
{
if ($subtype eq "x-empty") {
$res = "File erroed out - Is empty.";
}
else
{
system("/usr/lib/libreoffice/program/soffice.bin --headless --invisible --norestore --nolockcheck --convert-to pdf -outdir /tmp/ /tmp/$randomtext > /dev/null");
$printed = 0;
foreach ($i = 0; $i < 10000; $i++) {
if (-e "/tmp/$randomtext.pdf") {
system("lpr -r /tmp/$randomtext.pdf");
$printed = 1;
}
}
unlink("/tmp/$randomtext");
$res = "Document file";
if ($printed == 0) {
$res = $res . " -- ERROR";
}
}
}
}

if ($maintype eq "text") {
system("/usr/lib/libreoffice/program/soffice.bin --headless --invisible --norestore --nolockcheck --convert-to pdf -outdir /tmp/ /tmp/$randomtext  > /dev/null");
$printed = 0;
foreach ($i = 0; $i < 10000; $i++) {
if (-e "/tmp/$randomtext.pdf") {
system("lpr -r /tmp/$randomtext.pdf");
$printed = 1;
}
}
unlink("/tmp/$randomtext");
$res = "Text file";
if ($printed == 0) {
$res = $res . " -- ERROR";
}
}

if ($res eq "UNSUPPFORM") {
print "Unsupported format: $data";
}
else
{
print "Sucessfully sent job to printer: $res";
}

}
else
{
print "Content-Type: text/html\n\n<form action=\"print.cgi\" method=\"post\" enctype=\"multipart/form-data\"><input type=\"file\" name=\"print\"><input type=\"submit\" value=\"Print\"></form>";
}