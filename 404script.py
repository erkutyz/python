import urllib2, base64
from ntlm import HTTPNtlmAuthHandler

import getpass
import sys
import tempfile
import base64
import os
import datetime
import requests
from requests_ntlm import HttpNtlmAuth

path = '/intranet/'

if path not in sys.path:
    sys.path.append(path)

from net.dbhandler import DbHandler
from net.imagehandler import ImageHandler
from net.env import Environment

#CONSTANTS 
_ID = 0
_NAME = 1
_ITP_ID = 2
_PAGE_ID = 3
hostname = "hostname"

class Script(object):
    
    def is404v2(self,itp_id,user,password):
        #Auth with given credentials and Ntlm
        #this part works in windows but not in Linux but not deleted inc ase of need

        try:
            passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
            passman.add_password(None, hostname, user, password)
            auth_NTLM = HTTPNtlmAuthHandler.HTTPNtlmAuthHandler(passman)
            opener = urllib2.build_opener(auth_NTLM)
            urllib2.install_opener(opener)
            addition = "customers/%s/SitePages/Home.aspx" % (itp_id)
            url = hostname+addition
            response = urllib2.urlopen(url)
            if response.code == 404:
                return True
        except urllib2.HTTPError, e:
            print(e)
            if e.code == 404:
                return True
        return False


    def is404(self,itp_id,user,password):
        #Auth with given credentials and Ntlm
        #See if Dms Link returns 404
        # this method works both in windows and linux
        addition =''
        if itp_id is not None:
            addition = "customers/%s/SitePages/Home.aspx" % (itp_id)
        url = hostname+addition
        r = requests.get(url, auth=HttpNtlmAuth(user,password))

        return r.status_code

    def getCustomers(self):
        #Get all active customer info from
        #customer and customer_customer_db Database Tabke

        self.db.sql = ("SELECT ccd.id, ccd.name, ccd.itp_id, c.id "+
                        "FROM customer as c "+
	                        "LEFT OUTER JOIN customer_customer_db as ccd on ccd.id = c.customer_id  and ccd.archive = 0 "+
                        "WHERE c.customer_folder = 1   ORDER BY ccd.itp_id IS NULL ")
        self.db.executeSQL(1, 'fetchall')
        customers = self.db.result

        return customers
    
    def writeToFile(self,str,file):
        #Append given string into given file 

        f = open(file,'a')
        f.write(str)
        f.write("\n--------------------------")
        f.close() 

    def formInfoStr(self,itpId,id_,name,pageId):
       
        add = "Debitor Id is None"
        if itpId is not None:
            add = "Debitor Id: %s is cannot be found in DMS" % (itpId)
        if name is not None:
            name = name.encode('utf-8')
        str = "\n CustomerId : %s CustomerName : %s \n %s \n Customer Page: Customer Page%s \n" % (id_,name,add,pageId)
        return str

    def process(self,user,password,file_path):
        #Main Function

        f = open(file_path,'w')
        f.write("Invalid Links Date:%s \n\n" %(datetime.date.today()))
        f.close() 
        self.env = Environment(None)
       
        self.db = DbHandler(self.env)
        customers = self.getCustomers()
        for customer in customers:
            ItpId = customer[_ITP_ID]
            Id = customer[_ID]
            Name = customer[_NAME]
            PageID = customer[_PAGE_ID]
            if ItpId is None:
                self.writeToFile(self.formInfoStr(ItpId,Id,Name,PageID),file_path)
            elif self.is404(ItpId,user,password) == 404 :
                self.writeToFile(self.formInfoStr(ItpId,Id,Name,PageID),file_path)

    def find404(self):
        #Call the main function
        user = r''
        password = ''
        file_path = ''
        user = raw_input('User Name: ')
        password = getpass.getpass('Password:')
        while self.is404(None, user, password) == 401:
            print("Unauthorized User. Wrong User Name/Password")
            user = raw_input('User Name: ')
            password = getpass.getpass('Password:')
        file_path = os.getcwd()+"\\404s.txt"
        print("Finding 404 returning links. Please wait!")
        self.process(user,password,file_path)
        print("Finished. Found entries saved in: "+file_path)

a =Script() 
a.find404()







