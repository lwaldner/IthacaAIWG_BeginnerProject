import sqlite3
import re


class WebDB(object):

    def __init__(self, dbfile):
        """
        Connect to the database specified by dbfile.  Assumes that this
        dbfile already contains the tables specified by the schema.
        """
        self.dbfile = dbfile
        self.cxn = sqlite3.connect(dbfile)
        self.cur = self.cxn.cursor()

        self.execute("""CREATE TABLE IF NOT EXISTS CachedURL (
                                 id  INTEGER PRIMARY KEY,
                                 url VARCHAR,
                                 title VARCHAR,
                                 docType VARCHAR
                            );""")

        self.execute("""CREATE TABLE IF NOT EXISTS URLToItem (
                                 id  INTEGER PRIMARY KEY,
                                 urlID INTEGER,
                                 itemID INTEGER
                            );""")

        self.execute("""CREATE TABLE IF NOT EXISTS Item (
                                 id  INTEGER PRIMARY KEY,
                                 name VARCHAR,
                                 type VARCHAR
                            );""")

    def _quote(self, text):
        """
        Properly adjusts quotation marks for insertion into the database.
        """

        text = re.sub("'", "''", text)
        return text

    def _unquote(self, text):
        """
        Properly adjusts quotations marks for extraction from the database.
        """

        text = re.sub("''", "'", text)
        return text

    def execute(self, sql):
        """
        Execute an arbitrary SQL command on the underlying database.
        """
        res = self.cur.execute(sql)
        self.cxn.commit()

        return res

    ####----------####
    #### CachedURL ####

    def lookupCachedURL_byURL(self, url):
        """
        Returns the id of the row matching url in CachedURL.

        If there is no matching url, returns an None.
        """
        sql = "SELECT id FROM CachedURL WHERE URL='%s'" % (self._quote(url))
        res = self.execute(sql)
        reslist = res.fetchall()
        if reslist == []:
            return None
        elif len(reslist) > 1:
            raise RuntimeError('DB: constraint failure on CachedURL.')
        else:
            return reslist[0][0]

    def lookupCachedURL_byID(self, cache_url_id):
        """
        Returns a (url, docType, title) tuple for the row
        matching cache_url_id in CachedURL.

        If there is no matching cache_url_id, returns an None.
        """
        sql = "SELECT url, docType, title FROM CachedURL WHERE id=%d" \
              % (cache_url_id)
        res = self.execute(sql)
        reslist = res.fetchall()
        if reslist == []:
            return None
        else:
            return reslist[0]

    def lookupItem_ByURLID(self, url_id):
        """
        Returns an item from url id.

        """
        sql = "SELECT itemID FROM URLToItem WHERE urlID=%d" \
              % (url_id)
        res = self.execute(sql)
        reslist = res.fetchall()
        if reslist == []:
            return None
        else:
            item_id = reslist[0][0]
            sql2 = "SELECT name, type FROM Item WHERE id='%d'" \
                   % (item_id)
            res2 = self.execute(sql2)
            reslist2 = res2.fetchall()
            if reslist2 == []:
                return None
            else:
                return reslist2[0]

    def lookupItem(self, name, itemType):
        """
        Returns a Item ID for the row
        matching name and itemType in the Item table.

        If there is no match, returns an None.
        """
        sql = "SELECT id FROM Item WHERE name='%s' AND type='%s'" \
              % (self._quote(name), itemType)
        res = self.execute(sql)
        reslist = res.fetchall()
        if reslist == []:
            return None
        else:
            return reslist[0][0]

    def lookupUrlsForItem(self, name, itemType):
        """
        Returns urlIds and urls for item
        matching name and itemType in the Item table.
        If there is no match, returns an empty list.
        """
        itemId = self.lookupItem(self._quote(name), itemType)
        reslist = []
        results = list()
        if (itemId):
            sql = "SELECT urlId FROM UrlToItem WHERE itemId=%d" % itemId
            res = self.execute(sql)
            reslist = res.fetchall()
            for r in reslist:
                results.append(int(str(r).strip('(),')))
        return results

    def lookupURLToItem(self, urlID, itemID):
        """
        Returns a urlToItem.id for the row
        matching name and itemType in the Item table.

        If there is no match, returns an None.
        """
        sql = "SELECT id FROM UrlToItem WHERE urlID=%d AND itemID=%d" \
              % (urlID, itemID)
        res = self.execute(sql)
        reslist = res.fetchall()
        if reslist == []:
            return None
        else:
            return reslist[0]

    def deleteCachedURL_byID(self, cache_url_id):
        """
        Delete a CachedURL row by specifying the cache_url_id.

        Returns the previously associated URL if the integer ID was in
        the database; returns None otherwise.
        """
        result = self.lookupCachedURL_byID(cache_url_id)
        if result == None:
            return None

        (url, download_time, docType) = result

        sql = "DELETE FROM CachedURL WHERE id=%d" % (cache_url_id)
        self.execute(sql)
        return self._unquote(url)

    def insertCachedURL(self, url, docType=None, title=None):
        """
        Inserts a url into the CachedURL table, returning the id of the
        row.

        Enforces the constraint that url is unique.
        """
        if docType is None:
            docType = ""

        cache_url_id = self.lookupCachedURL_byURL(url)
        if cache_url_id is not None:
            return cache_url_id

        sql = """INSERT INTO CachedURL (url, docType, title)
                 VALUES ('%s', '%s','%s')""" % (self._quote(url), docType, title)

        res = self.execute(sql)
        return self.cur.lastrowid

    def insertItem(self, name, itemType):
        """
        Inserts a item into the Item table, returning the id of the
        row.
        itemType should be something like "music", "book", "movie"

        Enforces the constraint that name is unique.
        """

        item_id = self.lookupItem(name, itemType)
        if item_id is not None:
            return item_id

        sql = """INSERT INTO Item (name, type)
                 VALUES (\'%s\', \'%s\')""" % (self._quote(name), self._quote(itemType))

        res = self.execute(sql)
        return self.cur.lastrowid

    def insertURLToItem(self, urlID, itemID):
        """
        Inserts a item into the URLToItem table, returning the id of the
        row.
        Enforces the constraint that (urlID,itemID) is unique.
        """

        u2i_id = self.lookupURLToItem(urlID, itemID)
        if u2i_id is not None:
            return u2i_id

        sql = """INSERT INTO URLToItem (urlID, itemID)
                 VALUES ('%s', '%s')""" % (urlID, itemID)

        res = self.execute(sql)
        return self.cur.lastrowid

    def numURLToItem(self, itemID):
        """
        Returns a urlToItem.id for the row
        matching name and itemType in the Item table.
        If there is no match, returns an None.
        """
        sql = "SELECT count(*) FROM UrlToItem WHERE itemID=%d" \
              % (itemID)
        res = self.execute(sql)
        reslist = res.fetchall()
        if reslist == []:
            return None
        else:
            return reslist[0][0]

    def totalURLs(self):
        sql = "SELECT COUNT(*) FROM CachedURL"
        res = self.execute(sql)
        reslist = res.fetchall()
        if reslist == []:
            return None
        else:
            return reslist[0][0]

    def allURLids(self):
        results = list()
        sql = "SELECT id FROM CachedURL"
        res = self.execute(sql)
        reslist = res.fetchall()
        if reslist == []:
            return None
        else:
            for r in reslist:
                results.append(int(str(r).strip('(),')))
            return results


if __name__ == '__main__':
    db = WebDB('test.db')
    urlID = db.insertCachedURL("http://jimi.ithaca.edu/", "text/html", "JimiLab :: Ithaca College")
    itemID = db.insertItem("JimiLab", "Research Lab")
    u2iID = db.insertURLToItem(urlID, itemID)

    (url, docType, title) = db.lookupCachedURL_byID(urlID);

    print("Page Info: ", url, "\t", docType, "\t", title)