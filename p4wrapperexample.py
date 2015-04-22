class PerforceWrapper(object):
    '''Handles Perforce operations,
    the included wrappers for common operations to interact with them in a more pythonic fashion,
    connections are generated at object created and closed at object deletion.
    '''
----/----
    def isCheckedOutBy(self, filePath):
        '''
        returns a list of names of users with the file checked out or false
        '''
        status = self.filesStatus(filePath)[0]
        otherNames = [] # a list of all the other uses with the file checked out.
        if "otherOpen" in status:
            for numOthers in range(0,int(status["otherOpens"])):
                for name in status["otherOpen"]:
                    name.split("@")[0].split(".")
                    nameOut = name[0][0].upper() + name[0][1:].lower() + " " +\
                        name[1][0].upper() + name[1][1:].lower()
                    otherNames.append(nameOut)
            return otherNames
        return False
----/----
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