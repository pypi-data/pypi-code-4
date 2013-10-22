# -*- coding: utf-8 -*-
"""
Parsers and backends for PyChanDownloader
"""
import os, hashlib, re
from random import choice
from urllib import urlretrieve
from urllib2 import urlopen, HTTPError, URLError, Request
import sqlite3

from BeautifulSoup import BeautifulSoup

from Sveetchies.chan import __version__, __title__, ChanBackendError

DEFAULT_CHAN_BASE_URL = 'http://boards.4chan.org/'
DEFAULT_DB_FILENAME = "registry.db"
THREAD_TABLE_SQL = "CREATE TABLE chan_threads (id INTEGER PRIMARY KEY, canal VARCHAR(255), thread_id VARCHAR(55), image_id VARCHAR(255), url TEXT, path TEXT, checksum TEXT);"
ADD_THREAD_SQL = "INSERT INTO chan_threads (id, canal, thread_id, image_id, url, path, checksum) VALUES (NULL, ?, ?, ?, ?, ?, ?);"
TEST_EXIST_THREAD_ITEMID_SQL = "SELECT COUNT(*) FROM chan_threads WHERE canal = ? AND thread_id = ? AND image_id = ?;"
TEST_CHECKSUM_THREAD_ITEMID_SQL = "SELECT COUNT(*) FROM chan_threads WHERE checksum = ?;"

class FourChanDownloader(object):
    """
    Download all images embedded in the messages from a thread on a chanel.
    This version is configured for 4chan.
    Files are downloaded in a directory where a database of the messages scanned is also created. Thus, if the same thread is scanned over and over, only unsaved files are saved. To support a different channel, a new ChanDownloader needs to be implemented (usually, only `ChanDownloader.process_response` and `ChanDownloader.get_thread_content` need to be modified so they fit the different HTML   )
    
    """
    def __init__( self, logger, root_dir=None, target_dir=None, base_url=DEFAULT_CHAN_BASE_URL, 
                    thread_url_tpl='%s/res/%s', db_filepath=None, debug=False):
        """
        :type logger: object `Sveetchies.logger.LoggingInterface`
        :param logger:  Logger Object. Although it's passed as kwargs, it is mandatory.'
        
        :type root_dir: string
        :param root_dir: (optional) Root dir where the script runs. By default, current directory.
        
        :type target_dir: string
        :param target_dir: (optional) Directory where the images will be saved. None by default, thus a new directory is created automatically with a unique name in root_dir.
        
        :type base_url: string
        :param base_url: (optional) Base url of the channel. Starts with http:// and ends with a / .
        
        :type thread_url_tpl: string
        :param thread_url_tpl: (optional) Template string to build the relative url of the page. 2 args: one for the channel, one for the thread id
        
        :type db_filepath: string
        :param db_filepath: (optional) Path to the sqlite file. Empty by default, which implies the file will be created in the target directory under the name defined by `DEFAULT_DB_FILENAME`. If the file does not exist, it will be created.
        """
        if not root_dir:
            root_dir = os.getcwd()
        self.root_dir = root_dir
        self.base_url = base_url
        self.thread_url_tpl = thread_url_tpl
        self.db_filepath = db_filepath
        self.debug = debug
        self.checksum_mode = False
        
        self.image_ids = []
        self.image_contents = []
        
        self.logger = logger
        
        self.target_dir, self.db_path = self.get_target_dirpath(target_dir, db_filepath)
        
        self.logger.title( "===== PyChanDownloader =====" )
        self.logger.info( "Chan Base Url : %s" % base_url )
        self.logger.info( "Target : %s" % self.target_dir )
        self.logger.info( "DB File : %s" % self.db_path )
        
    def get_target_dirpath( self, target_dir=None, db_filepath=None ):
        """
        Calcul le chemin absolu vers le répertoire qui va contenir les fichiers à 
        téléchargés
        
        :type target_dir: string
        :param target_dir: (optional) Répertoire cible, vide par défaut, si il n'est pas 
                           spécifié, un nom unique sera généré
        
        :type db_filepath: string
        :param db_filepath: (optional) Nom de fichier pour la bdd
        
        :rtype: tuple
        :return: * (string) Chemin absolu du répertoire cible
                 * (string) Chemin absolu vers le fichier de BDD
        """
        if not target_dir:
            target_dir = ''
            for i in range(choice((5,6))):
                target_dir += choice("abdefghijklmnopqrstuvwxyz1234567890ABDEFGHIJKLMNOPQRSTUVWXYZ")
        target_path = os.path.join(self.root_dir, target_dir)
        
        if not db_filepath:
            db_filepath = os.path.join(target_path, DEFAULT_DB_FILENAME)
        
        return target_path, db_filepath
    
    def process( self, canal, thread_id ):
        """
        Image download processing. The images are in the thread/channel defined
        
        :type canal: string
        :param canal: Channel name
        
        :type thread_id: string
        :param thread_id: thread identifier
        """
        a = 0
        b = 0
        self.image_contents = []
        
        thread_url = os.path.join(self.base_url, self.thread_url_tpl%(canal, thread_id))
        response_info, response_content = self.process_request(thread_url)

        # Storage directory creation
        if not os.path.exists(self.target_dir):
            os.mkdir(self.target_dir, 0755)
        # Database opening
        self.opened_conn = sqlite3.connect( self.db_path )
        self.opened_conn.row_factory = sqlite3.Row
        self.check_db()

        soup = BeautifulSoup(response_content)
        self.process_response( canal, thread_id, soup )
        
        self.download_images( self.image_contents )
    
    def process_request(self, url, indent=''):
        """
        http request processing
        
        :type url: string
        :param url: Path of the command to be run
        
        :type indent: string
        :param indent: Identification string to be used in the info message
        
        :rtype: tuple
        :return: * File Meta data
                 * Content of the answer givent by the server.
        """
        self.logger.info("Request on url: %s" % url, indent=indent)
        
        req = Request(url)
        req.add_header('User-agent', __title__)
        
        try:
            f = urlopen(req)
        except HTTPError, e:
            self.logger.error(str(e))
            self.logger.error("Site send a HttpError")
            raise ChanBackendError
        except URLError, e:
            self.logger.error(str(e))
            self.logger.error("Site is unreachable")
            raise ChanBackendError
        else:
            return f.info(), f.read()
    
    def process_response( self, canal, thread_id, response_soup ):
        """
        Parsing o the BeautifulSoup document to look for images
        
        :type canal: string
        :param canal: Channel name
        
        :type thread_id: string
        :param thread_id: thread identifier
        
        :type response_soup: string
        :param response_soup: HTTP answer http
        """
        # Look for the thread container using its form (the form is used by admins to delete messages
        form_container = response_soup.find('form', attrs={"name" : "delform"})
        if not form_container:
            self.logger.error("Form container @name='delform' is unreachable")
        
        # First element of the thread
        first = self.get_thread_content( canal, thread_id, form_container )
        if first:
            self.image_contents.append( first )
        
        # All answers in the thread are tables with no attributes
        lambda_finder = lambda tag: tag.name=='table' and len(tag.attrs) == 0
        for item in form_container.findAll(lambda_finder, recursive=False):
            item_content = item.tr.find('td', attrs={"class" : "reply"})
            content = self.get_thread_content( canal, thread_id, item_content )
            if content:
                self.image_contents.append( content )

    def get_thread_content( self, canal, thread_id, soup_element ):
        """
        Parses and get the content of a thread in case it contains an image.
        
        :type canal: string
        :param canal: Channel name 
        
        :type thread_id: string
        :param thread_id: thread identifier
        
        :type soup_element: object `BeautifulSoup.Tag`
        :param soup_element: ``Tag`` Element from a message
        
        :rtype: dict or None
        :return: message content elements
        """
        thread_img_link = soup_element.find("a", recursive=False)
        # No link means no images. Skip
        if thread_img_link:
            url = thread_img_link.get('href', None)
            img_id = os.path.basename( url ).split('.')[0]
            filename = os.path.basename(url)
            thread_starter_title_container = soup_element.find("span", { "class" : "filesize" })
            if thread_starter_title_container:
                filename = thread_starter_title_container.find("span").get('title', None)
            
            return {
                'id': img_id,
                'site': self.base_url,
                'canal': canal,
                'thread_id': thread_id,
                'filename': filename,
                'url': url,
            }
        return None

    def download_images(self, image_list):
        """
        Starts the download of all elements
        
        :type image_list: list
        :param image_list: list of images dictionnaries selected by the parser.
        """
        self.logger.info("%s images finded"%len(image_list), indent="  * ")
        for img in image_list:
            target_filename, target_filepath = self.get_image_filename(self.target_dir, img['filename'])
            deb = "%s) %s > %s" % (img['id'], img['url'], target_filename)
            self.logger.info(deb, indent="    * ", lv=2)
            self.get_file(img, target_filename, target_filepath)
        
    def get_file( self, file_dict, filename, filepath):
        """
        Downloads and saves the file in a register if it's valid
        
        Creates a checksum of the file for further checksum comparison
        
        :type file_dict: dict
        :param file_dict: dictionary that contains all information for the message : (id, url, retrieved file name, aso.)
        
        :type filename: string
        :param filename: file name as it must be created on the disk(incremented if a file already exists).
        
        :type filepath: string
        :param filepath: Absolut path that includes the name of the file to be created
        """
        if not self.item_allreadyexist_validator(file_dict['canal'], file_dict['thread_id'], file_dict['id']):
            # Save the file
            if not self.debug:
                #urlretrieve(file_dict['url'], filepath)
                info, content = self.process_request(file_dict['url'], indent="      - ")
                size = "%sKo" % (int(info['Content-Length'])/1024)
                self.logger.info(size, indent="        > ", lv=2)
                md5 = hashlib.md5()
                md5.update(content)
                file_hash = md5.hexdigest()
                if not self.item_checksum_validator(file_hash):
                    # Saves the file on disk
                    downloaded_file = file(filepath, "wb")
                    downloaded_file.write(content)
                    downloaded_file.close()
                    # Add an entry in the database
                    self._cursor = self.opened_conn.cursor()
                    self._cursor.execute(ADD_THREAD_SQL, (file_dict['canal'], file_dict['thread_id'], file_dict['id'], file_dict['url'], filepath, file_hash))
                    self.opened_conn.commit()
                    self._cursor.close()
                else:
                    self.logger.info("[Pass] An image with the same checksum allready exist", indent="      - ", lv=2)
        else:
            self.logger.info("[Pass] Image ID allready exist", indent="      - ", lv=2)
        
    def check_db( self ):
        """
        Checks wether the database exists, and if not, creates it
        """
        self._cursor = self.opened_conn.cursor()
        
        self._cursor.execute("SELECT * FROM sqlite_master WHERE 1;")
        test_existing_tables = [tbl[2] for tbl in self._cursor.fetchall() if tbl[0]=='table' and tbl[2] in ['chan_threads']]
        # No database found. Tables created
        if len(test_existing_tables)==0:
            self.logger.info( "New Database created" )
            self._cursor.execute(THREAD_TABLE_SQL)
            self.opened_conn.commit()
        
        self._cursor.close()
    
    def item_allreadyexist_validator(self, canal, thread_id, image_id, checksum=None):
        """
        Checks wether an image (after its identier) has not already been saved for the same thread and the same channel
        
        :type canal: string
        :param canal: Channel name
        
        :type thread_id: string
        :param thread_id: thread identifier
        
        :type image_id: string
        :param image_id: Image identifier
        
        :type checksum: string
        :param checksum: 
        
        :rtype: bool
        :return: True if the image has already been saved. False otherwise.
        """
        queryset = self._cursor.execute(TEST_EXIST_THREAD_ITEMID_SQL, (canal, thread_id, image_id))
        if queryset.fetchone()[0]>0:
            return True
        return False
    
    def item_checksum_validator(self, checksum):
        """
        Checks that an identical image (comparison by checksum) has not already been saved in the registry (irrespective of thread, channel)
        
        :type checksum: string
        :param checksum: 
        
        :rtype: bool
        :return: True if an identical image already exists. False otherwise
        """
        queryset = self._cursor.execute(TEST_CHECKSUM_THREAD_ITEMID_SQL, (checksum,))
        if queryset.fetchone()[0]>0:
            return True
        return False
    
    def get_image_filename(self, target_dir, filename):
        """
        Downloads all elements. Do not check wether it's an image or anything else.
        
        :type target_dir: string
        :param target_dir: Absolute path to the directory where the file will be saved.
        
        :type filename: string
        :param filename: Name of the file found in the message.
        
        :rtype: tuple
        :return: * Name of the file to be created;
                 * Absolute path to where to create the file.
        """
        if os.path.exists( os.path.join(target_dir, filename) ):
            i = len([item for item in os.listdir(target_dir) if item.startswith(filename.split('.')[0])])
            filename = '.'.join( [filename.split('.')[0], str(i)] + filename.split('.')[1:] )
            
        return filename, os.path.join(target_dir, filename)

class ZeroChanDownloader(FourChanDownloader):
    def __init__( self, logger, root_dir=None, target_dir=None, base_url="http://zerochan.org/", 
                    thread_url_tpl='%s/res/%s', db_filepath=None, debug=False):
        
        self.image_text_regex = re.compile("\(.*\)$")
        self.image_title_regex = re.compile("(.*)(\()(.*)(\).*)$")
        
        super(ZeroChanDownloader, self).__init__(
            logger, 
            root_dir=root_dir, 
            target_dir=target_dir, 
            base_url=base_url, 
            thread_url_tpl='%s/res/%s.html', 
            db_filepath=db_filepath, 
            debug=debug
        )

    def process_response( self, canal, thread_id, response_soup ):
        """
        Parses the BeautifulSoup document to find images in the messages
        
        :type canal: string
        :param canal: channel name
        
        :type thread_id: string
        :param thread_id: thread identifier
        
        :type response_soup: string
        :param response_soup: HTTP response HTML
        """
        # Look for the thread container by its form (which is a deletion form for admins)
        form_container = response_soup.find('form', attrs={"id" : "delform"})
        if not form_container:
            self.logger.error("Form container @id='delform' is unreachable", error_blocker=True)
        
        # First thread element
        first = self.get_thread_content( canal, thread_id, form_container.div )
        if first:
            #print first
            self.image_contents.append( first )
        
        # All thread answers ar attributeless tables
        lambda_finder = lambda tag: tag.name=='table' and len(tag.attrs) == 0
        for item in form_container.div.findAll(lambda_finder, recursive=False):
            item_content = item.tr.find('td', attrs={"class" : "reply"})
            #print item_content
            content = self.get_thread_content( canal, thread_id, item_content )
            if content:
                #print content
                self.image_contents.append( content )

    def get_thread_content( self, canal, thread_id, soup_element ):
        """
        Parses and get the content of a message in the thread, if it contains an image
        
        :type canal: string
        :param canal: Channel name
        
        :type thread_id: string
        :param thread_id: thread identifier
        
        :type soup_element: object `BeautifulSoup.Tag`
        :param soup_element: ``Tag`` element in a message
        
        :rtype: dict or None
        :return: message content elements
        """
        #self.logger.info("[Pass] Image ID allready exist", indent="      - ", lv=2)
        lambda_finder = lambda tag: tag.name=='a' and 'href' in [a[0] for a in tag.attrs] and 'onclick' not in [a[0] for a in tag.attrs]
        thread_img_link = soup_element.findAll(lambda_finder, recursive=False)
        # No link means no image. We go next.
        if len(thread_img_link)>0:
            thread_img_link = thread_img_link[0]
            # Source link
            url = thread_img_link.get('href', None)
            if url.startswith('/'): 
                url = url[1:]
            url = self.base_url+url
            # identifier after the automatic name of the online file
            img_id = os.path.basename( url ).split('.')[0]
            # Destination filename
            filename = os.path.basename(url)
            # Container for the original name for the online file
            thread_starter_title_container = soup_element.find("span", { "class" : "filesize" })
            if thread_starter_title_container:
                foo = thread_starter_title_container.find(text=self.image_text_regex)
                g = self.image_title_regex.match(foo).group(3)
                filename = g.split(',')[-1].strip()
                
            return {
                'id': img_id,
                'site': self.base_url,
                'canal': canal,
                'thread_id': thread_id,
                'filename': filename,
                'url': url,
            }
        return None

class IChanDownloader(FourChanDownloader):
    def __init__( self, logger, root_dir=None, target_dir=None, base_url="http://ichan.org/", 
                    thread_url_tpl='%s/res/%s', db_filepath=None, debug=False):
        
        self.image_text_regex = re.compile("\(.*\)$")
        self.image_title_regex = re.compile("(.*)(\()(.*)(\).*)$")
        
        super(IChanDownloader, self).__init__(
            logger, 
            root_dir=root_dir, 
            target_dir=target_dir, 
            base_url=base_url, 
            thread_url_tpl='%s/res/%s.html', 
            db_filepath=db_filepath, 
            debug=debug
        )

    def process_response( self, canal, thread_id, response_soup ):
        """
        Parses the BeautifulSoup document for images in the messages
        
        :type canal: string
        :param canal: Channel name
        
        :type thread_id: string
        :param thread_id: thread identifier
        
        :type response_soup: string
        :param response_soup: HTTP Answer HTML
        """
        # Look for the thread container by its form (which is a deletion form for admins)
        form_container = response_soup.find('form', attrs={"id" : "delform"})
        if not form_container:
            self.logger.error("Form container @id='delform' is unreachable", error_blocker=True)
        
        # First thread element
        first = self.get_thread_content( canal, thread_id, form_container )
        if first:
            self.image_contents.append( first )
        
        #All thread answers are attributeless tables
        lambda_finder = lambda tag: tag.name=='table' and len(tag.attrs) == 0
        for item in form_container.findAll(lambda_finder, recursive=False):
            item_content = item.tr.find('td', attrs={"class" : "reply"})
            #print item_content
            content = self.get_thread_content( canal, thread_id, item_content )
            if content:
                #print content
                self.image_contents.append( content )

    def get_image_link( self, url ):
        """
        Cleanup of the url of an image source
        
        TODO: Put it in the base class and use it
        
        :type url: string
        :param url: url extracted from the html
        
        :rtype: string
        :return: Cleaned URL
        """
        #Transforms relative url into absolute ones
        if url.startswith('/') and not url.startswith('http'):
            url = url[1:]
            url = self.base_url+url
        # remove the redirections
        parts = [item for item in url.split('http') if len(item)>0]
        if len(parts)>1:
            url = 'http'+parts[-1]
        return url

    def get_thread_content( self, canal, thread_id, soup_element ):
        """
        Parses and gets the content of a message of a thread if it contains an image.
        
        :type canal: string
        :param canal: Channel name
        
        :type thread_id: string
        :param thread_id: thread identifier
        
        :type soup_element: object `BeautifulSoup.Tag`
        :param soup_element: ``Tag`` element of a message
        
        :rtype: dict or None
        :return: Message content elements
        """
        # Works only for the first thread
        thread_img_element = soup_element.findAll('div', attrs={"class" : "threadimg"}, recursive=False)
        # Fallback for the answers in the thread
        if len(thread_img_element)==0:
            lambda_finder = lambda tag: tag.name=='a' and 'href' in [a[0] for a in tag.attrs] and 'onclick' not in [a[0] for a in tag.attrs]
            thread_img_element = soup_element.findAll(lambda_finder, recursive=False)
        # No image, we go next.
        if len(thread_img_element)>0:
            #thread_img_link = thread_img_link[0]
            thread_starter_title_container = soup_element.find("span", { "class" : "filesize" })
            #Link to the source
            url = self.get_image_link( thread_starter_title_container.find('a').get('href') )
            # identifier after the automatic name of the online file
            img_id = os.path.basename( url ).split('.')[0]
            # Destination file name
            filename = os.path.basename(url)
            # Container of the original online file name
            title_link = thread_starter_title_container.find("a", recursive=False)
            if title_link:
                filename = title_link.string.strip()
                
            return {
                'id': img_id,
                'site': self.base_url,
                'canal': canal,
                'thread_id': thread_id,
                'filename': filename,
                'url': url,
            }
        return None
