#This file is part of seur. The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.

from seur.utils import seur_url

from xml.dom.minidom import parseString
import urllib2
import os
import genshi
import genshi.template

loader = genshi.template.TemplateLoader(
    os.path.join(os.path.dirname(__file__), 'template'),
    auto_reload=True)


class API(object):
    """
    Generic API to connect to seur
    """
    __slots__ = (
        'url',
        'username',
        'password',
        'vat',
        'in5',
        'in7',
        'ci',
        'ccc',
    )

    def __init__(self, username, password, vat, in5, in7, ci, ccc, debug=False):
        """
        This is the Base API class which other APIs have to subclass. By
        default the inherited classes also get the properties of this
        class which will allow the use of the API with the `with` statement

        Example usage ::

            from seur.api import API

            with API(username, password) as seur_api:
                return seur_api.test_connection()

        :param username: API username of the Seur Web Services.
        :param password: API password of the Seur Web Services.
        :param vat: company vat
        :param in5: franchise code
        :param in7: identification description
        :param ci: franchise code
        :param ccc: identification description
        """
        self.url = seur_url(debug)
        self.username = username
        self.password = password
        self.vat = vat
        self.in5 = in5
        self.in7 = in7
        self.ci = ci
        self.ccc = ccc

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        return self

    def connect(self, method, xml):
        """
        Connect to the Webservices and return XML data from seur

        :param method: method service.
        :param xml: XML data.
        
        Return XML object
        """
        url = '%s%s' % (self.url, method)
        headers={}
        request = urllib2.Request(url, xml, headers)
        response = urllib2.urlopen(request)
        return response.read()

    def test_connection(self):
        """
        Test connection to Seur webservices
        Send XML to Seur and return error send data
        """
        tmpl = loader.load('test_connection.xml')

        vals = {
            'username': self.username,
            'password': self.password,
            'vat': self.vat,
            'in5': self.in5,
            'in7': self.in7,
            }

        method = 'ImprimirECBWebService'
        xml = tmpl.generate(**vals).render()
        result = self.connect(method, xml)
        dom = parseString(result)

        #Get message connection
        #username and password wrong, get error message
        #send a shipment error, connection successfully
        message = dom.getElementsByTagName('mensaje')
        if message:
            msg = message[0].firstChild.data
            if msg == 'ERROR':
                return 'Connection successfully'
            return msg
        return 'Not found message attribute from %s XML' % method
