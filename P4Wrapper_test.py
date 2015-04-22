# unit test module is what runs the functions for testing
import unittest
# helper modules that assist in setting up elements for testing
import os
#module to test
import perforce.P4Wrapper as wrapper;reload(wrapper)

class TestPerforceConnection(unittest.TestCase):

    '''
    These tests verify that the perforce functionality is being accessed correctly, 
    They will help verify if any changes have broken core p4 functionality,
    Because they are reliant on the external P4Python API they do not reveal much about the system functionality
    '''
    
    def setUp(self):
        '''
        Setup before every test case, these are re-initialized between tests.
        Any elements that are needed across all the tests that must be setup before tests can be run. 
        '''
        self.perforceObject = wrapper.PerforceWrapper()
        # some testing file paths, nothing permenent should be done to them, 
        # replace with more generic paths in the future.
        self.filePaths = ["//maya_tools/HI_Tools/site-package/perforce/test/file1.txt"
                    , "//maya_tools/HI_Tools/site-package/perforce/test/file2.txt"
					, "//maya_tools/HI_Tools/site-package/perforce/test/file3.txt"
                    ]
        self.filePath = 'e:/Workspace/Perforce/maya_tools/HI_Tools/site-package/perforce/test/file1.txt'
        self.fileStats = []
        
    def tearDown(self):
        '''
        Tear down anything used by the test so the next test can run on a clean state.
        This removes all the variablres are used in the test to ensure that they no longer exist
        '''
        del self.perforceObject
        del self.fileStats
        del self.filePath
        del self.filePaths
        
    def test_connection(self):
        '''
        open a connection, rely on the destructor to close the connection
        '''
        self.perforceObject.connectionOpen()
        connection = self.perforceObject.connected
        self.assertTrue(connection,"The connection was not opened.")
    
    def test_disconnection(self):
        '''
        open a connection and ensure that the connection is closed by checking the connection status change (bool)
        '''
        self.perforceObject.connectionOpen()
        self.perforceObject.connectionClose()
        connected = self.perforceObject.connected
        #connectionOpen - are we connected? should be false, small chance of none which is also false 
        self.assertFalse(connected,"The connection remaines open.")
    
    def test_openFilesForEdit(self):
        '''
        using dummy file paths in the depot, these will need to be changed per workspace,
        once p4 where is working this may be something that could be done with depot paths, though it will invalidate the isolation of the tests
        check to see if the edit func checks out the files properly
        '''
        self.perforceObject.connectionOpen()
        #checkout some files, check their status and revert them.
        edit = self.perforceObject.edit(self.filePaths)
        fileStats = self.helper_filesStatus(self.filePaths,os.W_OK,False) #check that the files are okay for writing, which is W_OK False
        revert = self.perforceObject.revert(self.filePaths)
        self.assertTrue(fileStats,"The files were not all checked out (made writeable with p4 edit)")
            
    def test_revertFiles(self):
        '''
        using the same dummy file paths, open some files for edit and then revert them
        '''
        self.perforceObject.connectionOpen()
        self.perforceObject.edit(self.filePaths)
        self.perforceObject.revert(self.filePaths)
        fileStats = self.helper_filesStatus(self.filePaths,os.W_OK,False) #check that the files are locked which is W_OK False
        self.assertTrue(fileStats, "Files are still writable, may still be open for edit or set to +w.")
    
    def test_add(self):
        '''
        check if a file can be added to perforce, 
        it will also need to be removed from the depot to make the test a clean validation cycle
        this will bloat the server slightly so it tests with an empty file 
        
        >>> touch file
        >>> p4 status file - should be not in perforce
        >>> p4 add file
        >>> p4 status file - should be marked for add
        >>> p4 revert file
        pass the test if the file was added
        '''
        f  = open(self.filePath, 'a+')
        f.close()
        self.perforceObject.add(self.filePath)
        fstat = self.perforceObject.filesStatus(self.filePath)[0]
        self.assertEqual( fstat['action'], 'add', 'File was not added to the depot')
        os.remove(self.filePath)
        self.perforceObject.revert(self.filePath)
        
    #def test_delete(self):
    #    '''
    #    tests the file removal functionality of the library, 
    #    this needs to be reliable for the teardown of the add test.
    #    '''
    #    self.perforceObject.delete(self.filePaths)
    #    fileStats = self.helper_filesStatus(self.filePaths[0], os.F_OK, False)
    #    self.assertTrue(fileStats, "Files were not deleted.")
    #    self.perforceObject.revert(self.filePaths)
    
    def test_opened(self):
        '''
        honestly unsure how to test this at the moment, 
        checkout some files, check opened files to see if those files are in a changelist
        the opened function should return a cl and filename for each file that is opened
        or even better 
        {
        cl:(fi,les),
        cl:(fi,les)
        }
        '''
        self.perforceObject.edit(self.filePaths) #open some files to see if they get returned
        openFiles = self.perforceObject.opened()
        #print openFiles
        found = False
        for inFile in openFiles:
            #print "inFile", inFile,openFiles
            if inFile["depotFile"] in self.filePaths:
                found = True
        self.assertTrue(found, msg="The files were not found open in the user's workspace.")
     
    def test_createChangeList(self):
        cl = self.perforceObject.createChangeList(description = 'Test CL 0',files = [])#,files = "//IGT/ZODI/Game/_testSubmitFile.txt")
        self.failUnless(type(cl) == type(int()), "The function did not return a change list Number")
        self.perforceObject.deleteChangeLists(cl)

    def test_update(self):
        result = self.perforceObject.update()
        if result != None:
            result = result[0]['action']
        if result == None or result == 'updated':
            self.assertTrue(True, "Files are up to date.")
        
    def test_submitChangelist(self):
        cl = self.perforceObject.createChangeList(
            description = "AUTO: TEST - testing changelist based submission"
            )
        result = self.perforceObject.submitChangelist(cl)
        self.perforceObject.deleteChangeLists(cl)

    def test_submit(self):
        if self.helper_filesStatus(self.filePath, os.F_OK):
            cl_add = self.perforceObject.edit(files = self.filePath)
        else:
            f  = open(self.filePath, 'a+')
            f.close() 
            cl_add = self.perforceObject.add(self.filePath)
        try:
            cl_submit = self.perforceObject.submit(
                description = "AUTO: TEST - testing python add"
                )
        except wrapper.P4Exception, e:
            for e in self.perforceObject.warnings:
                print e
            for e in self.perforceObject.errors:
                print e
        cl = self.perforceObject.delete(files = self.filePath)
        self.perforceObject.submit(
            changelist = cl
            , description = "AUTO: TEST - testing python remove"
            )
        
    #dummyish tests, this only ensure that the functions run but do not test any of the values.
    def test_isCheckedOut(self):
        self.perforceObject.isCheckedOut(self.filePath)
        pass
    def test_isCheckedOutBy(self):
        #these files are locked always checked out, using auto builder file
        self.assertTrue(self.perforceObject.isCheckedOutBy("//rush-wml/working/NG-S0124-Autobuild.wset"))
        pass 
    def test_isCheckedOutBySelf(self):
        self.perforceObject.edit()
        status = self.perforceObject.isCheckedOutBySelf(self.filePaths[1])
        print status
        pass         
    def test_isOpenForAdd(self):
        self.perforceObject.isOpenForAdd(self.filePath)
        pass
    def test_isOpenForEdit(self):
        self.perforceObject.isOpenForEdit(self.filePath)
        pass
    def test_isOpenForDelete(self):
        self.perforceObject.isOpenForDelete(self.filePath)
        pass
    def test_isLatest(self):
        self.perforceObject.isLatest(self.filePath)
        pass

    def test_areCheckedOut(self):
        self.perforceObject.areCheckedOut(self.filePaths)
        pass
    def test_areCheckedOutBy(self):
        #these files are locked always checked out, using auto builder files
        self.perforceObject.areCheckedOutBy([
            "//rush-wml/working/NG-S0124-Autobuild.wset",
            "//rush-wml/working/NG-S0131-Autobuild.wset"
        ])
        pass    
    
    def test_areOpenForAdd(self):
        self.perforceObject.areOpenForAdd(self.filePaths)
        pass
    def test_areOpenForEdit(self):
        self.perforceObject.areOpenForEdit(self.filePaths)
        pass
    def test_areOpenForDelete(self):
        self.perforceObject.areOpenForDelete(self.filePaths)
        pass
    def test_areLatest(self):
        self.perforceObject.areLatest(self.filePaths)
        pass
    ## Helper functions
    def helper_filesStatus(self,fileList,status , boolean = True):
        '''
        Helper function that checks a list of files to see if they match a given status
        if they have a given status it returns True if any of the files match
        True or false can be passed in to change which status is relevant, 
        returns True if the status with te state of boolean is found in the file list.
        i.e. 
        F_OK , False) will return True if any of the files do not exist
        '''
        _bool = bool
        stats = []
        fileList = self.perforceObject._toList(fileList)
        for path in fileList:
            stats.append(self.helper_fileStatus(
                path
                ,status
                )
            )
            _bool = boolean in stats   # this simplefies the check return to a single bool value
        return _bool

    def helper_fileStatus(self,filePath,status):
        '''
        Helper function that returns if the file status for a given status request
        F_OK - file exists? does the file exist at the given path
        W_OK - write okay? does the file exist and is it writableable to write the file 
        R_OK - Read okay? If the file exists can it be read from
        '''
        return os.access(filePath,status)
class TestPerforceWrapper(unittest.TestCase):
    '''
    Test custom functionality that has no reliance on the external perfore library
    These tests verify that functions are doing what are designed to do.    
    '''
    def setUp(self):
        self.perforceObject = wrapper.PerforceWrapper()
    
    def tearDown(self):
        del self.perforceObject
    
    def test_toList(self):
        string = str()
        result = self.perforceObject._toList(string)
        self.assertEqual(result,[str()])

    def test_tryFunction(self):
        ex = self.helper_genericFunction
        _input = 'C:/'
        self.assertEqual(
            str
            , self.perforceObject._tryFunction(
                ex,_input
                )
            )

    def helper_genericFunction(self, *args):
        return type(*args)

    def helper_genericExcpetionThrowingFunction(self, *args):
        '''
        Test the excpetion handling of a function
        '''
        raise(
            wrapper.P4Exception(
                "Dummy Error, {0}".format(
                    args
                    )
                )
            )
    
if __name__ == '__main__':
    unittest.main()
