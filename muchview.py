#!/usr/bin/env python
# -*- coding: utf8 -*-
'''
Created on 2012/4/28
@author: ethan

@Histories:
2012-05-16:
* Add all item_url to mongodb, then step by step to get capture url.
* Add skip capture when this item duplicate in mongodb.

2012-05-29:
* Download product images to location folder
* Add print capture log format to YAML (easy_install PyYAML)

2012-06-06:
* change mongodb to mysql, because openvz not support mongodb.

2012-06-12:
* Add capture next page

2012-06-13:
* Fixed capture next page and previous problems.
* urllib request move to function
  def request(self, url) return html
* add log function
  def logger(self, str): open(... write close...

2012-06-23"
* add agents_items_user_reviews table, and add the function to Muchview module.
* Modify category support sub-category layer.


CREATE TABLE `agents` (
	`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
	`source_name` VARCHAR(50) NOT NULL,
	`capture_start_time` DATETIME NOT NULL,
	`capture_end_time` DATETIME NOT NULL,
	`capture_items_num` INT(10) NOT NULL DEFAULT '0',
	`capture_images_num` INT(10) NOT NULL DEFAULT '0',
    `capture_images_error_num` INT(10) NOT NULL DEFAULT '0',
	`language` VARCHAR(10) NOT NULL,
	`category_by_this_agent` VARCHAR(10) NOT NULL,
	PRIMARY KEY (`id`),
	INDEX `id` (`id`),
	INDEX `source_name` (`source_name`)
)
COMMENT='agent sites'
COLLATE='utf8_general_ci'
ENGINE=InnoDB;

CREATE TABLE `agents_categories` (
	`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
	`source_name` VARCHAR(50) NOT NULL,
	`category_name` VARCHAR(50) NOT NULL,
	`category_url` TEXT NOT NULL,
	`capture_datetime` DATETIME NOT NULL,
	`capture_done` VARCHAR(10) NOT NULL DEFAULT 'N/A',
	PRIMARY KEY (`id`),
	INDEX `id` (`id`),
	INDEX `source_name` (`source_name`)
)
COMMENT='agents categories'
COLLATE='utf8_general_ci'
ENGINE=InnoDB;

CREATE TABLE `agents_items` (
	`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
	`source_name` VARCHAR(50) NOT NULL,
	`category_name` VARCHAR(50) NOT NULL,
	`category_url` TEXT NOT NULL,
	`items_name` TEXT NOT NULL,
	`items_url` TEXT NOT NULL,
	`capture_datetime` DATETIME NOT NULL,
	`capture_done` VARCHAR(10) NOT NULL DEFAULT 'N/A',
	PRIMARY KEY (`id`),
	INDEX `id` (`id`),
	INDEX `source_name` (`source_name`)
)
COMMENT='agents items'
COLLATE='utf8_general_ci'
ENGINE=InnoDB;


CREATE TABLE `agents_items_attrs` (
	`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
	`source_name` VARCHAR(50) NOT NULL,
	`items_name` TEXT NOT NULL,
	`items_url` TEXT NOT NULL,
	`logo` TEXT NOT NULL,
	`title` TEXT NOT NULL,
	`desc` TEXT NOT NULL,
	`offical_url` TEXT NOT NULL,
	`cates` TEXT NOT NULL,
	`rating` TEXT NOT NULL,
	`price` TEXT NOT NULL,
	`capture_datetime` DATETIME NOT NULL,
	PRIMARY KEY (`id`),
	INDEX `id` (`id`),
	INDEX `source_name` (`source_name`)
)
COMMENT='agents items attribute'
COLLATE='utf8_general_ci'
ENGINE=InnoDB;


CREATE TABLE `agents_items_images` (
	`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
	`source_name` VARCHAR(50) NOT NULL,
	`items_url` TEXT NOT NULL,
	`images_key` TEXT NOT NULL,
	`images_url` TEXT NOT NULL,
	`capture_datetime` DATETIME NOT NULL,
	PRIMARY KEY (`id`),
	INDEX `id` (`id`)
)
COMMENT='agents items images'
COLLATE='utf8_general_ci'
ENGINE=InnoDB;

CREATE TABLE `agents_items_spec` (
	`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
	`source_name` VARCHAR(50) NOT NULL,
	`items_url` TEXT NOT NULL,
	`spec_key` TEXT NOT NULL,
	`spec_url` TEXT NOT NULL,
	`capture_datetime` DATETIME NOT NULL,
	PRIMARY KEY (`id`),
	INDEX `id` (`id`)
)
COMMENT='agents items specfication'
COLLATE='utf8_general_ci'
ENGINE=InnoDB;

CREATE TABLE `agents_items_user_reviews` (
	`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
	`source_name` VARCHAR(50) NOT NULL,
	`items_url` TEXT NOT NULL,
	`author` TEXT NOT NULL,
	`author_comment` TEXT NOT NULL,
    `rating` TEXT ,
	`review_datetime` TEXT ,
    `capture_datetime` DATETIME NOT NULL,
	PRIMARY KEY (`id`),
	INDEX `id` (`id`)
)
COMMENT='User review for agent items'
COLLATE='utf8_general_ci'
ENGINE=InnoDB;

CREATE TABLE `agents_items_user_reviews_pros` (
	`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
	`source_name` VARCHAR(50) NOT NULL,
	`items_url` TEXT NOT NULL,
	`pros_key` TEXT,
	`pros_value` TEXT,
	PRIMARY KEY (`id`),
	INDEX `id` (`id`),
	INDEX `source_name` (`source_name`)
)
COMMENT='agents_items_user_reviews_pros'
COLLATE='utf8_general_ci'
ENGINE=InnoDB;


@Roadmap:
* Add recapture when remote URL deny our request.
* Add write to log file.
'''
from lxml import etree
import urllib2
import datetime
import pprint
import yaml
import os
import MySQLdb
import MySQLdb.cursors
import time
import pickle


host='localhost'
user='User_for_User'
passwd='Password_for_MySQL'
db='muchview'

class MuchViewEngine:
    def __init__(self, url):
        #self.user_agent = 'Mozilla/5.0 (Windows NT 6.1; rv:5.0) Gecko/20100101 Firefox/5.02011-10-16 20:21:42'
        self.user_agent = 'Mozilla/5.0 (Windows; U; MSIE 9.0; WIndows NT 9.0; en-US)'
        self.previous_nextpage_url = None
        self.next_page_try_count = 0
        self.en = None
        #connect to mysql
        self.conn = None
        self.cursor = None
        self.short_url = None
        self.duplicate_delete = False
        self.url = url
        
        opener = urllib2.build_opener()
        request = urllib2.Request(self.url)
        request.add_header('User-Agent',self.user_agent)
        self.html = opener.open(request).read()
        '''
        u = urllib2.urlopen(self.url)
        self.html = u.read()
        '''
        self.parser = etree.HTMLParser(encoding=self.en)
        self.categories = []
        self.categories_url = []
        self.items = []
        self.items_url = []
        self.source_name = None
        self.language = None
        self.category_by_this_agent = None
        #self.conn = pymongo.Connection('localhost', 27017)
        #self.db = self.conn['MuchView']
        self.capture_items_num = 0
        self.capture_images_num = 0
        self.current_category = None
        #opener.close()

    def create_agent(self):
        self.conn = MySQLdb.connect(host=host,user=user,passwd=passwd,db=db,cursorclass=MySQLdb.cursors.DictCursor)
        self.cursor = self.conn.cursor()
        self.conn.set_character_set(self.en)
        
        self.cursor.execute("select source_name from agents where source_name = '%s'" % self.source_name)
        row = self.cursor.fetchall()
        if not row:
            now = datetime.datetime.now()
            self.cursor.execute("""
            insert into agents values(null,'%s','%s','%s',0,0,0,0,'%s','%s')
            """ % (self.source_name, now, now, self.language, self.category_by_this_agent))
            self.conn.commit()
        
    def cates(self, path, txt, val, process_sub_category=False,replace_url_1=False):
        tree = etree.fromstring(self.html, self.parser)
        data = tree.xpath(path)
        for link in data:
            if link.xpath(val)[0].count('http://') == 0 and  link.xpath(val)[0].count('https://')  == 0:
                if replace_url_1:
                    _replace_url = link.xpath(val)[0].replace('../','')
                else:
                    _replace_url = link.xpath(val)[0]
                url = self.short_url + _replace_url
                
            else:
                url = link.xpath(val)[0]
            #set current category url and name
            self.categories_url.append( url )
            self.categories.append( urllib2.quote(link.xpath(txt)[0].encode(self.en)) )

            self.cursor.execute("select source_name,category_url from agents_categories where source_name = '%s' and category_url = '%s'" % (self.source_name, url))
            row = self.cursor.fetchall()
            if not row:
                try:
                    now = datetime.datetime.now()
                    SQL = """
                    insert into agents_categories values (null,'%s','%s','%s','%s','N/A')
                    """ % (self.source_name, urllib2.quote(link.xpath(txt)[0].encode(self.en)), url, now)
                    self.cursor.execute(SQL)
                except:
                    print '***ERROR =>', SQL

            self.conn.commit()
            
        if process_sub_category:
            for c_url in self.categories_url:
                html = self.request(c_url)
                if not html:
                    return False
                parser = etree.HTMLParser(encoding=self.en)
                tree = etree.fromstring(html, parser)
                
                data = tree.xpath(path)
                for link in data:
                    if link.xpath(val)[0].count('http://') == 0 and  link.xpath(val)[0].count('https://')  == 0:
                        if replace_url_1:
                            _replace_url = link.xpath(val)[0].replace('../','')
                        else:
                            _replace_url = link.xpath(val)[0]
                        url = self.short_url + _replace_url
                    else:
                        url = link.xpath(val)[0]
                    #set current category url and name
                    self.categories_url.append( url )
                    self.categories.append( urllib2.quote(link.xpath(txt)[0].encode(self.en)) )

                    self.cursor.execute("select source_name,category_url from agents_categories where source_name = '%s' and category_url = '%s'" % (self.source_name, url))
                    row = self.cursor.fetchall()
                    if not row:
                        try:
                            now = datetime.datetime.now()
                            SQL = """
                            insert into agents_categories values (null,'%s','%s','%s','%s','N/A')
                            """ % (self.source_name, urllib2.quote(link.xpath(txt)[0].encode(self.en)), url, now)
                            self.cursor.execute(SQL)
                        except:
                            print '***ERROR =>', SQL
                    self.conn.commit()            
                    
    def process_agent_items_nextpage(self, data, tree, path,  txt,  val, ci, c_url, nextpage=None,  attrs=None):
        if nextpage:
            data = tree.xpath(nextpage)
            if data:
                if data[0].count('http://') == 0 and  data[0].count('https://')  == 0:
                    #c_url = self.short_url + data[0]
                    c_url = self.url + data[0]
                else:
                    c_url = data[0]
                next_page = data[0]

                self.logger('DEBUG:', 'Process next page => %s' % next_page)
                self.logger('DEBUG:', 'Previous page =>%s' % self.previous_nextpage_url)
                
                if (next_page == self.previous_nextpage_url):
                    self.next_page_try_count += 1
                if (next_page == self.previous_nextpage_url) and (self.next_page_try_count >= 2):
                    self.logger('DEBUG:', 'Process next page %s == previous_nextpage_url %s' % (next_page,  self.previous_nextpage_url))
                    return False
                    
                if next_page != self.previous_nextpage_url:
                    self.previous_nextpage_url = next_page
                    self.logger('DEBUG:', 'Set Previous page = next_page')

                html = self.request(c_url)
                #try:
                #    opener = urllib2.build_opener()
                #    request = urllib2.Request(c_url)
                #    request.add_header('User-Agent',self.user_agent)
                #    html = opener.open(request).read()
                #except Exception as e:
                #    print 'ERROR request next page =>',  e,  c_url
                if not html:
                    return False
                parser = etree.HTMLParser(encoding=self.en)
                tree = etree.fromstring(html, parser)
                
                #inital items container again
                self.items = []
                self.items_url = []
                
                #print "path",  path
                data = tree.xpath(path)
                for link in data:
                    if link.xpath(txt) != []:
                        if link.xpath(val)[0].count('http://') == 0 and link.xpath(val)[0].count('https://') == 0:
                            url = self.short_url + link.xpath(val)[0]
                        else:
                            url = link.xpath(val)[0]
                        self.items_url.append( url )
                        self.items.append( urllib2.quote(link.xpath(txt)[0].encode(self.en)) )
                        #print "url",  url
                        #print "txt",  link.xpath(txt)[0]
                        self.cursor.execute("select source_name,items_url from agents_items where source_name = '%s' and items_url = '%s'" % (self.source_name, url))
                        row = self.cursor.fetchall()
                        if not row:
                            #try:
                                now = datetime.datetime.now()
                                #print ci
                                #print txt, link.xpath(txt)
                                #print urllib2.quote(link.xpath(txt)[0].encode(self.en))
                                SQL = """
                                insert into agents_items values (null,'%s','%s','%s','%s','%s','%s','N/A')
                                """ % (self.source_name, ci, c_url, urllib2.quote(link.xpath(txt)[0].encode(self.en)), url, now)
                                self.cursor.execute(SQL)
                                self.conn.commit()
                            #except:
                            #    print '***ERROR =>', SQL
                #time.sleep(1)
                if attrs:
                    self.attrs(attrs)
                return self.process_agent_items_nextpage(data, tree, path,  txt,  val, ci, c_url, nextpage=nextpage, attrs=attrs)
                    
    def agent_items(self, path, txt, val, nextpage=None, replace_url_1=False, attrs=None):
        if self.categories_url:
            for ci, c_url in enumerate(self.categories_url): #[:2]
                self.current_category = self.categories[ci]
                if c_url.count('http://') == 0 and c_url.count('https://') == 0:

                    if replace_url_1:
                        _replace_url = c_url.replace('../','')
                    else:
                        _replace_url = c_url
                    c_url = self.short_url + _replace_url

                
                    #c_url = self.short_url + c_url
                self.logger('DEBUG:', 'Category Request => %s' % c_url)
                #print 'Category Request =>', c_url  
                #try:
                #    opener = urllib2.build_opener()
                #    request = urllib2.Request(c_url)
                #    request.add_header('User-Agent',self.user_agent)
                #    html = opener.open(request).read()
                #except Exception as e:
                #    print 'ERROR Category Request =>',  e,  c_url

                html = self.request(c_url)
                if not html:
                    return False
                parser = etree.HTMLParser(encoding=self.en)
                tree = etree.fromstring(html, parser)
                data = tree.xpath(path)
                
                #inital items container again
                self.items = []
                self.items_url = []
                for link in data:
                    if link.xpath(txt) != []:
                        if link.xpath(val)[0].count('http://') == 0 and link.xpath(val)[0].count('https://') == 0:
                            url = self.short_url + link.xpath(val)[0]

                            if replace_url_1:
                                _replace_url = link.xpath(val)[0].replace('../','')
                            else:
                                _replace_url = link.xpath(val)[0]
                            url = self.short_url + _replace_url
                        
                        else:
                            if replace_url_1:
                                url = link.xpath(val)[0].replace('../','')
                            else:
                                url = link.xpath(val)[0]
                        self.items_url.append(''.join( url ))
                        self.items.append( urllib2.quote(link.xpath(txt)[0].encode(self.en)) )

                        self.cursor.execute("select source_name,items_url from agents_items where source_name = '%s' and items_url = '%s'" % (self.source_name, url))
                        row = self.cursor.fetchall()
                        if not row:
                            #try:
                                now = datetime.datetime.now()
                                #print self.categories[ci]
                                #print txt, link.xpath(txt)
                                #print urllib2.quote(link.xpath(txt)[0].encode(self.en))
                                SQL = """
                                insert into agents_items values (null,'%s','%s','%s','%s','%s','%s','N/A')
                                """ % (self.source_name, self.categories[ci], c_url, urllib2.quote(link.xpath(txt)[0].encode(self.en)), url, now)
                                self.cursor.execute(SQL)
                                self.conn.commit()
                                
                            #except:
                            #    print '***ERROR =>', SQL
                
                #time.sleep(1)
                if attrs:
                    self.attrs(attrs)
                if nextpage:
                    self.process_agent_items_nextpage(data, tree, path,  txt,  val,  self.categories[ci], c_url,  nextpage=nextpage, attrs=attrs)
                
    def attrs(self, path):
        if self.items_url:
            SQL = """update agents set capture_start_time='%s',capture_end_time='%s' where source_name = '%s'""" % (self.source_name,datetime.datetime.now(),datetime.datetime.now())
            #print SQL
            self.cursor.execute(SQL)
            self.conn.commit()
            self.logger('DEBUG:', pickle.dumps(self.items))
            #for __x in self.items_url:
            #    print __x.__class__
            self.logger('DEBUG:', pickle.dumps(self.items_url))
            for i,url in enumerate(self.items_url): #[:2]
                #print "select source_name,items_url from agents_items_attrs where source_name = '%s' and items_url = '%s'" % (self.source_name, url)
                self.cursor.execute("select source_name,items_url from agents_items_attrs where source_name = '%s' and items_url = '%s'" % (self.source_name, url))
                row = self.cursor.fetchall()
                if not row:
                    #try:
                        self.logger('DEBUG:', 'Attr Request => %s' % url)
                        #print 'Attr Request =>', url
                        
                        #html = ''
                        #try:
                        #    opener = urllib2.build_opener()
                        #    request = urllib2.Request(url)
                        #    request.add_header('User-Agent',self.user_agent)
                        #    html = opener.open(request).read()
                        #except Exception as e:
                        #    print 'ERROR Attr Request =>',  e,  url
                        html = self.request(url)
                        if not html:
                            return False
                        parser = etree.HTMLParser(encoding=self.en)
                        tree = etree.fromstring(html, parser)
                        c = {}
                        for k in path.keys():
                            c['source_name'] = self.source_name
                            c['items_url'] = url
                            
                            if type(path[k]) == str:
                                data = tree.xpath(path[k])
                                if data and k != 'desc':
                                    c[k] = ''.join(data)
                                elif data and k == 'desc':
                                    _desc = ''
                                    for d in data:
                                        _desc += d
                                        c[k] = ''.join(_desc)
                                if k == 'logo':
                                    if c.has_key('logo'):
                                        if c[k].count('http://') == 0 and c[k].count('https://') == 0:
                                            ck_url = self.short_url + c[k]
                                        else:
                                            ck_url = c[k]
                                    else:
                                        return False

                                    in_memory = self.request(self.tostring(ck_url))
                                    if not in_memory:
                                        return False

                                    #try:
                                    #    opener = urllib2.build_opener()
                                    #    request = urllib2.Request(ck_url)
                                    #    request.add_header('User-Agent',self.user_agent)
                                    #    in_memory = opener.open(request).read()
                                    #except Exception as e:
                                    #    print 'ERROR Request logo =>',  e,  ck_url

                                    #download_image = urllib2.urlopen(c[k])
                                    #in_memory = download_image.read()
                                    if in_memory:
                                        if not os.path.isdir('%s/%s' % (os.getcwd(), self.source_name)):
                                            os.mkdir('%s/%s' % (os.getcwd(), self.source_name))
                                        f = open('%s/%s/%s' % (os.getcwd(),self.source_name, ck_url.split('/')[-1]), 'wb+')
                                        f.write(in_memory)
                                        f.close()
                            elif type(path[k]) == dict and k !='user_review':
                                c[k+'_key'] = []
                                c[k+'_value'] = []
                                data = tree.xpath(path[k]['path'])
                                for link in data:
                                    if path[k].has_key('key'):
                                        if path[k]['key'] != None:
                                            _k = link.xpath( path[k]['key'] )
                                            if _k:
                                                c[k+'_key'].append( ''.join(_k) )
                                    if path[k].has_key('value'):
                                        _v = link.xpath( path[k]['value'] )
                                        if _v:
                                            c[k+'_value'].append( ''.join(_v) )
                                            if k == 'images':
                                                if _v[0].count('http://') == 0 and _v[0].count('https://') == 0:
                                                    img_url = self.short_url + _v[0]
                                                else:
                                                    img_url = _v[0]
                                                
                                                if path[k].has_key('process'):
                                                    if path[k]['process'].split("|")[0] == "value":
                                                        img_url = eval("'"+img_url+"'"+path[k]['process'].split("|")[1])
                                                #print "Request images =>",  img_url
                                                self.logger('DEBUG:', 'Request images => %s' % img_url)
                                                in_memory = self.request(img_url)
                                                if not in_memory:
                                                    return False
                                                #try:
                                                #    opener = urllib2.build_opener()
                                                #    request = urllib2.Request(img_url)
                                                #    request.add_header('User-Agent',self.user_agent)
                                                #    in_memory = opener.open(request).read()
                                                #except Exception as e:
                                                #    print "ERROR Request images =>",  e,  img_url

                                                #download_image = urllib2.urlopen(_v[0])
                                                #in_memory = download_image.read()
                                                try:
                                                    if not os.path.isdir('%s/%s' % (os.getcwd(), self.source_name)):
                                                        os.mkdir('%s/%s' % (os.getcwd(), self.source_name))
                                                    f = open('%s/%s/%s' % (os.getcwd(),self.source_name, url.split('/')[-1]), 'wb+')
                                                    f.write(in_memory)
                                                    f.close()
                                                    self.capture_images_num += 1
                                                except:
                                                    self.logger('ERROR:', 'Create image file => %s' % _v[0])
                                                    #print "*** ERROR CAPTURE IMAGE ***", _v[0]
                            elif type(path[k]) == dict and k =='user_review': 
                                data = tree.xpath(path[k]['path'])
                                if path[k].has_key('author'):
                                    c[k+'_author'] = []
                                if path[k].has_key('author_comment'):
                                    c[k+'_author_comment'] = []
                                if path[k].has_key('review_datetime'):
                                    c[k+'_review_datetime'] = []
                                if path[k].has_key('rating'):
                                    c[k+'_rating'] = []
                                for link in data:
                                    if path[k].has_key('author'):
                                        _a = link.xpath( path[k]['author'] )
                                        if _a:                                            
                                            c[k+'_author'].append( ''.join(_a) )        
                                    if path[k].has_key('author_comment'):
                                        _ac = link.xpath( path[k]['author_comment'] )
                                        if _ac:                                            
                                            c[k+'_author_comment'].append( ''.join(_ac) )        
                                    if path[k].has_key('review_datetime'):
                                        _rd = link.xpath( path[k]['review_datetime'] )
                                        if _rd:
                                            c[k+'_review_datetime'].append( ''.join(_rd) )
                                    if path[k].has_key('rating'):
                                        _rt = link.xpath( path[k]['rating'] )
                                        if _rt:
                                            c[k+'_rating'].append( ''.join(_rt) )
                                    if path[k].has_key('pros_path'):
                                        _pp = link.xpath( path[k]['pros_path'] )
                                        c[k+'_pros_key'] = []
                                        c[k+'_pros_value'] = []
                                        if _pp:
                                            for link1 in _pp:
                                                _ppk = link1.xpath( path[k]['pros_key'] )
                                                if _ppk:
                                                    c[k+'_pros_key'].append( ''.join(_ppk) )
                                                _ppv = link1.xpath( path[k]['pros_value'] )
                                                if _ppv:
                                                    c[k+'_pros_value'].append( ''.join(_ppv) )
                                                
                                                try:
                                                    self.cursor.execute("""select items_url from agents_items_attrs where items_url = '%s'""" % c['items_url'])
                                                    row = self.cursor.fetchall()
                                                    if not row:
                                                        SQL = """insert into agents_items_user_reviews_pros values(null,'%s','%s','%s','%s')""" \
                                                        % (c['source_name'],
                                                           c['items_url'],                                       
                                                           urllib2.quote(''.join(_ppk).encode(self.en)),
                                                           urllib2.quote(''.join(_ppv).encode(self.en))
                                                           )
                                                        #print SQL
                                                        self.cursor.execute(SQL)
                                                        self.conn.commit()
                                                except:
                                                    return False
                                                
                        self.logger('DEBUG:',pickle.dumps(c))
                        #print yaml.dump(c, default_flow_style=False)
                        #print """select items_url from agents_items_attrs where items_url = '%s'""" % c['items_url']
                        self.cursor.execute("""select items_url from agents_items_attrs where items_url = '%s'""" % c['items_url'])
                        row = self.cursor.fetchall()
                        if not row:
                            if c.has_key('offical_url'):
                                _offical_url = c['offical_url']
                            else:
                                _offical_url = None
                            if c.has_key('price'):
                                _price = urllib2.quote(c['price'].strip().encode(self.en))
                            else:
                                _price = None
                            if c.has_key('rating'):
                                _rating = urllib2.quote(c['rating'].strip().encode(self.en))
                            else:
                                _rating = None
                            if c.has_key('desc'):
                                try:
                                    _desc = urllib2.quote(c['desc'].strip().encode(self.en))
                                except:
                                    _desc = urllib2.quote(c['desc'].strip().encode('utf8'))
                            else:
                                _desc = None
                            if c.has_key('logo'):
                                _logo = c['logo']
                            else:
                                _logo = None
                            SQL = """insert into agents_items_attrs values(null,'%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')""" \
                            % (c['source_name'],
                               urllib2.quote(c['title'].strip().encode(self.en)),
                               c['items_url'],
                               _logo,
                               urllib2.quote(c['title'].strip().encode(self.en)),
                               _desc,
                               _offical_url,
                               urllib2.quote(c['cates'].strip().encode(self.en)),
                               _rating,
                               _price,
                               datetime.datetime.now())
                            #print SQL
                            self.cursor.execute(SQL)
                            self.conn.commit()
                            if c.has_key('images_value'):
                                for iu_index, iu in enumerate(c['images_value']):
                                    try:
                                        _imagekey = urllib2.quote(c['images_key'][iu_index].encode(self.en))
                                    except:
                                        _imagekey = None
                                    SQL = """insert into agents_items_images values(null,'%s','%s','%s','%s','%s')""" \
                                    % (c['source_name'],
                                       c['items_url'],
                                       _imagekey,
                                       urllib2.quote(iu.encode(self.en)),
                                       datetime.datetime.now())
                                    #print SQL
                                    self.cursor.execute(SQL)
                                    self.conn.commit()
                            if c.has_key('spec_value'):
                                for sk_index, sk in enumerate(c['spec_value']):
                                    try:
                                        _speckey = urllib2.quote(c['spec_key'][sk_index].encode(self.en))
                                    except:
                                        _speckey = None
                                    try:    
                                        SQL = """insert into agents_items_spec values(null,'%s','%s','%s','%s','%s')""" \
                                        % (c['source_name'],
                                           c['items_url'],                                       
                                           _speckey,
                                           urllib2.quote(sk.encode(self.en)),
                                           datetime.datetime.now())
                                        #print SQL
                                        self.cursor.execute(SQL)
                                        self.conn.commit()
                                    except:
                                        return False
                            if c.has_key('user_review_author_comment'):
                                for sk_index, sk in enumerate(c['user_review_author_comment']):
                                    try:
                                        _author = urllib2.quote(c['user_review_author'][sk_index].encode(self.en))
                                    except:
                                        _author = None
                                    try:
                                        _author_comment = urllib2.quote(c['user_review_author_comment'][sk_index].encode(self.en))
                                    except:
                                        _author_comment = None
                                    try:
                                        _review_datetime = urllib2.quote(c['user_review_review_datetime'][sk_index].encode(self.en))
                                    except:
                                        _review_datetime = None
                                    try:
                                        _rating = urllib2.quote(c['user_review_rating'][sk_index].encode(self.en))
                                    except:
                                        _rating = None
                                    try:    
                                        SQL = """insert into agents_items_user_reviews values(null,'%s','%s','%s','%s','%s','%s','%s')""" \
                                        % (c['source_name'],
                                           c['items_url'],                                       
                                           _author,
                                           _author_comment,
                                           _rating,
                                           _review_datetime,
                                           datetime.datetime.now())
                                        #print SQL
                                        self.cursor.execute(SQL)
                                        self.conn.commit()
                                    except:
                                        return False
                        #update agents_items capture statue from N/A to done.
                        SQL = """update agents_items set capture_done = 'done',capture_datetime='%s' where items_url = '%s' """ % (datetime.datetime.now(), c['items_url'])
                        #print SQL
                        self.cursor.execute(SQL)
                        self.conn.commit()
                        self.capture_items_num += 1
                        
                        SQL = """select category_url from agents_items where items_url ='%s' """ % (c['items_url'])
                        #print SQL
                        self.cursor.execute(SQL)
                        cate_row = self.cursor.fetchall()
                        if cate_row:
                            #print cate_row
                            self.current_category = cate_row[0]['category_url']
                            SQL = """update agents_categories set capture_datetime='%s', capture_done='processing' where category_url = '%s'""" % \
                                  (datetime.datetime.now(), cate_row[0]['category_url'])
                            #print SQL
                            self.cursor.execute(SQL)
                            self.conn.commit()

                        SQL = """update agents set capture_end_time='%s', capture_items_num=%d, capture_images_num=%d where source_name = '%s'""" % \
                              (datetime.datetime.now(), self.capture_items_num, self.capture_images_num, c['source_name'])
                        #print SQL
                        self.cursor.execute(SQL)
                        self.conn.commit()
                        '''
                        now = datetime.datetime.now()
                        SQL = """
                        insert into agents_items_attrs values (null,'%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')
                        """ % (self.source_name,
                               self.items[i],
                               url,
                               urllib2.quote(link.xpath(txt)[0].encode(self.en)),
                               link.xpath(val)[0],
                               now)
                        self.cursor.execute(SQL)
                        self.conn.commit()
                        '''
                    #except :
                    #    print '*** ERROR CAPTURE ***', url
            #update capture_end_time
            SQL = """update agents set capture_end_time='%s' where source_name = '%s'""" % (self.source_name,datetime.datetime.now())
            #print SQL
            self.cursor.execute(SQL)
            self.conn.commit()
            
            SQL = """
            select 
            count(*) as "total_num",
            b.process_num,
            case when b.process_num = count(*) then
            'true'
            else
            'false'
            end as "done_ok"
            from agents_items a,
            (
            select count(*) as "process_num" from agents_items where category_name = '%s' and capture_done='done'
            ) b
            where 
            a.category_name = '%s'
            """ % (self.current_category, self.current_category)
            #print SQL
            self.cursor.execute(SQL)
            process_row = self.cursor.fetchall()
            if process_row:
                if process_row[0]['done_ok'] == 'true':
                    SQL = """update agents_categories set capture_datetime='%s', capture_done='done' where source_name = '%s' and category_name = '%s'""" % \
                          (datetime.datetime.now(), self.source_name, self.current_category)
                    #print SQL
                    self.cursor.execute(SQL)
                    self.conn.commit()
            #time.sleep(1)            

    def logger(self, t, e):
        now = str(datetime.datetime.now())
        f = open('%s/%s-%s.log' % (os.getcwd(), self.source_name, now[:10]),'a+')
        f.write('%s: %s => %s \n' % (t,now,e))
        f.close()
    def request(self, url):
        try:
            try:
                self.logger('DEBUG:', url)
                opener = urllib2.build_opener()
                request = urllib2.Request(url)
                request.add_header('User-Agent',self.user_agent)
                html = opener.open(request).read()
                return html
            except:
                self.logger('DEBUG: Request use urlopen', url)
                u = urllib2.urlopen(url)
                html = u.read()
                return html
        except Exception as e:
            self.logger('ERROR:',e)
            SQL = """update agents set capture_items_error_num=capture_items_error_num+1 where source_name = '%s'""" % (self.source_name)
            self.cursor.execute(SQL)
            self.conn.commit()
            return False


    def tostring(self, s):
        tmp = s.replace("'","")
        return tmp
