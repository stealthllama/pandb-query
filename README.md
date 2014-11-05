pandb-query
===========

A tool for bulk URL queries against Palo Alto Networks' PAN-DB cloud database

Requirements:
----
* pan-python - Multi-tool set for Palo Alto Networks PAN-OS, Panorama and WildFire

Usage:
----
<pre>
pandb-query.py [-h] [-u USERNAME] [-p PASSWORD] [-f FIREWALL] [-t TAG]
                      [-i INFILE] [-o OUTFILE]

optional arguments:
  -h, --help            show this help message and exit
  -u USERNAME, --username USERNAME
                        administrator username
  -p PASSWORD, --password PASSWORD
                        administrator password
  -f FIREWALL, --firewall FIREWALL
                        firewall hostname or IP address
  -t TAG, --tag TAG     firewall tag from the .panrc file
  -i INFILE, --infile INFILE
                        input file of URLs
  -o OUTFILE, --outfile OUTFILE
                        output file
</pre>
