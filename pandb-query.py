import argparse
import getpass
from pan.xapi import *


'''
Script Name: urlcheck
Author: Robert Hagen - https://github.com/stealthllama/pandb-query
    Adapted by: Arlo Hollingshad
Version Number: 1.0
Language Version: 3.8
Description of Function: This script takes a file with a list of URLs and checks the Palo Alto URL database on the
local firewall, and the Cloud URL database
'''


def make_parser():
    """
    This function takes the command line inputs and returns them in variables the rest of the script will use.
    :return: All arguments passed into the Command line
    """
    # Parse the arguments
    parser = argparse.ArgumentParser(description="Bulk PAN-DB URL lookup utility")
    parser.add_argument("-u", "--username", help="administrator username")
    parser.add_argument("-p", "--password", help="administrator password")
    parser.add_argument("-f", "--firewall", help="firewall hostname or IP address")
    parser.add_argument("-t", "--tag", help="firewall tag from the .panrc file", default='')
    parser.add_argument("-i", "--infile", help="input file of URLs", default='')
    parser.add_argument("-o", "--outfile", help="output file", default='')
    args = parser.parse_args()
    return args


def read_file(filename):
    """
    This function takes a file name, and opens a file in read-only mode.
    :param filename: Name of the file to be opened
    :return: File object in read-only mode
    """
    try:
        infilehandle = open(filename, 'r')
        return infilehandle
    except IOError:
        print("Error: Cannot open file %s" % filename)


def write_file(filename):
    """
    This function takes a file name and opens a file in write mode.
    :param filename: Name of the file to be opened
    :return: File object in write mode
    """
    try:
        outfilehandle = open(filename, 'w')
        return outfilehandle
    except IOError:
        print("Error: Cannot open file %s" % filename)


def make_key(user, pswd, firewall):
    """

    :param user: API-enabled username for connecting to Palo Alto firewall
    :param pswd: Password for the user specified above
    :param firewall: IP address of the firewall to be connected to
    :return: A connection object, which includes the API key for making new calls to the firewall.
    """
    newconn = PanXapi(api_username=user, api_password=pswd, hostname=firewall)
    newconn.keygen()
    return newconn


def get_url(fwconn, url):
    """

    :param fwconn: Connection object, needs to include the API key
    :param url: URL to find categories for
    :return: Output of test url <url> command
    """
    try:
        fwconn.op(cmd="<test><url>%s</url></test>" % url)
    except PanXapiError:
        print('Bad URL: ', url)
    return fwconn


def make_pretty(elem):
    """
    This function takes the result of the URL lookup, and returns the local and cloud discovered categories
    :param elem: URL lookup result. Output from get_url function.
    :returns local_category: URL category returned by URL database locally on firewall
    :returns cloud_category: URL category returned by Palo Alto Cloud URL database
    """
    try:
        result = elem.text.split('\n')
        local = result[0]
        cloud = result[1]
    except AttributeError:
        return 'not-resolved'
    local_category = local.split(' ')[1]
    cloud_category = cloud.split(' ')[1]
    return local_category, cloud_category


def main(**kwargs):
    """
    This the main script activity. It pulls in the
    :param kwargs: Only used when not running in command line mode. Valid Keyword arugments:
        firewall: IP address/hostname for the firewall to connect to
        username: API enabled user to sign in to the above firewall
        password: Password for the user specified above
        infile: Input file with list of URLs
        outfile: Output file for URL lookup results (default results.csv)
    """
    # Grab the args
    myargs = make_parser()
    bad_urls = write_file('BadUrls.txt')
    # Open the input file
    if 'infile' in kwargs:
        infile = read_file(kwargs['infile'])
        with read_file(kwargs['infile']) as file:
            line_count = sum(1 for line in file)
    elif myargs.infile:
        infile = read_file(myargs.infile)
        with read_file(myargs.infile) as file:
            line_count = sum(1 for line in file)
    else:
        infile = sys.stdin
        with read_file(sys.stdin) as file:
            line_count = sum(1 for line in file)

    # Open the output file
    if 'outfile' in kwargs:
        outfile = write_file(kwargs['outfile'])
    elif myargs.outfile:
        outfile = write_file(myargs.outfile)
    else:
        outfile = sys.stdout

    # Open a firewall API connection
    if 'tag' in kwargs:
        myconn = PanXapi(tag=kwargs['tag'])
    elif myargs.tag:
        # Use the .panrc API key
        myconn = PanXapi(tag=myargs.tag)
    else:
        # Generate the API key
        # if 'username'
        if 'firewall' and 'username' and 'password' in kwargs:
            myconn = make_key(kwargs['username'], kwargs['password'], kwargs['firewall'])
        else:
            myconn = make_key(myargs.username, myargs.password, myargs.firewall)

    # Iterate through the URL list, perform the lookup, and print the result
    outfile.write('URL,Local Category,Cloud Category\n')
    count = 0
    for myurl in infile:
        count += 1
        get_url(myconn, myurl.strip())
        try:
            local_cat, cloud_cat = make_pretty(myconn.element_result)
            outfile.write(f'{myurl.strip()},{local_cat},{cloud_cat}\n')
            outfile.flush()
        except ValueError:
            bad_urls.write(f'{myurl.strip()}\n')
        if count % 10 == 0:
            print(f'{count}/{line_count}')

    # Close the input file
    if infile is not sys.stdin:
        infile.close()

    # Close the output file
    if outfile is not sys.stdout:
        outfile.close()


# Enables script to be run as a traditional script rather than the command line
if __name__ == '__main__':
    args = make_parser()
    if not len(sys.argv) > 1:
        hostname = input('Enter the IP of the firewall: ')
        username = input('Enter the username: ')
        password = getpass.getpass()
        file_in = input('Enter the text file with URLs: ')
        main(firewall=hostname, username=username, password=password, infile=file_in, outfile='results.csv')
    else:
        main()
