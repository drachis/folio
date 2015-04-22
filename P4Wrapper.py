'''
author: "Toli Carter"
email: "toli.carter@heavy-iron.com"
This is a wrapper for the p4 library for python

The purpose of this wrapper is to improve the ease of use for perfoce functions, 
and ensure they are well intragted for use in other scripts.
'''
#testing p4 commits, 
from P4 import P4, P4Exception

class PerforceWrapper(object):
    '''Handles Perforce operations,
    the included wrappers for common operations to interact with them in a more pythonic fashion,
    connections are generated at object created and closed at object deletion.
    '''
    def __init__(self):
        '''
            Setup the connection to the server when the object is instanciated
        '''
        self.perforce = P4()        
        self.connectionOpen()

    def __del__(self):
        '''
            Close the connection to perforce when the object is garbage collected,
            If the connection is already closed die gracefuly.
        '''
        self.connectionClose()

    #make common information easier to access through the use of @property
    @property
    def user(self):
        '''
        Returns the name of the active user
        '''
        return self.perforce.user

    @property
    def client(self):
        '''
        Returns the name of the active workspace.
        '''
        return self.perforce.client

    @property
    def clientRoot(self):
        '''
        Return the location of the base of the user's workspace
        '''
        return self.info[0]["clientRoot"]

    @property
    def clientHost(self):
        '''
        Returns the name of the user's machine
        '''
        return self.info[0]["clientHost"]
    
    @property
    def connected(self):
        '''
        Returns the connection status
        '''
        return self.perforce.connected()

    @property
    def info(self):
        '''
        Returns information on the current user and workspace from perforce
        '''
        return self._tryFunction(self.perforce.run_info)

    def _toList(self, data):
        '''
        Allows for both strings or ints as input as either a list or solo
        a list of the input object wil be returned, 
        creates compatability for _extendList for more inputs
        '''
        outFiles = []
        if (type(data) == str or type(data) == unicode or type(data) == type(int())):
            outFiles.append(data)
        else:
            outFiles.extend(data)
        return outFiles
        
    def _extendList(self, data, _list):
        '''Extends the given _list with the data provided
        this works on non list data as an input with the use of __toList
        extend vs append works as follows;
        extend:
        [file1, file2 ].extend([file3]) =
        [file1, file2, file3]
        append:
        [file1, file2 ].append([file3]) =
        [file1, file2, [file3]]

        '''
        filesList = self._toList(data)
        return _list.extend(filesList)

    # These are not used yet (__convertPath & __initFileStatus & __initStatusDict)
    # The intention is to help pass data around in a cleaner fashion for large requests
    # For these to work error handling had to be done in a different fashion.
    def _convertPath(self,filePath):
        if filePath.startswith("//depot"):
            return filePath.lower()
        return os.path.abspath(filePath).lower()
    
    def _initFileStatus(self, filePath):
        '''
        creates a dictionary to store file status information
        '''
        fileDict = {
            "exists" : False
            , "read-only": True
            , "status": None
            , "error" : None
            , "path" : filePath
        }
        return fileDict

    def _initStatusDict(self, filePaths):
        '''
        create a dictionary of dictionaries that contains 
        the files as keys and the status for different properties as a sub dict
        '''
        status = {}
        filePaths = self._toList(filePaths)
        for filePath in filePaths:
            convertedPath = self._convertPath(filePath)
            status[convertedPath] = self._initFileStatus(filePath)
        return status
    
    def _tryFunction(self, function, *args):
        '''
        Run a given function with given args and diffuse any errors, 
        This is similar to:
        p4 function args
        '''
        results = None
        try:
            # *args maps the input to the function paramaters
            # no args is okay for functions with no input params
            results = function(*args)
        except P4Exception, e:
            for e in self.perforce.warnings:
                print e
            for e in self.perforce.errors:
                print e
        return results
    
    def _runFunction(self, function, files=None, changelist=None, *args):
        '''
        Runs a function with the given arguments
        This is similar to:
        p4 function (args) (changelist) (files)
        on the command line.
        '''
        ## some functions will be passing in additional flags
        ## make a local extendable (list) _args, the passed args is a tuple
        ## this should handle an empty args list for functions with no input as well
        _args = []
        _args.extend(args)
        # Changelist and Files are part of the input for the majority of the functions in perforce
        # run command on an existing changelist
        if(changelist != None):
            _args.extend(["-c", changelist])
        # add files for the function to act on
        if files != None:
            self._extendList(files,_args)
        results = self._tryFunction(
            function
            , _args
            )
        return results  

    def connectionClose(self):
        '''
        Close the perforce connection.
        Only attempt to disconnect if there is an open connection.
        NOTE: For connections to the internal Perforce server the connection remains open
        '''
        if self.connected:
            self.perforce.disconnect()       
        return self.connected
    
    def connectionOpen(self):
        '''
            Initiate the connection to the perforce server
            only attempt to disconnect if the connection is open.
        '''
        if not self.connected:
            self.perforce.connect()
        return self.connected

    def edit(self, files=None, changelist=None):
        '''Open a file or files for edit returns a change list
            intended to work on a list of files
            because batching file operation is faster            
        ''' 
        _args = []
        if changelist != None:
            self._extendList(["-c",changelist],_args)
        if files != None:
            self._extendList(files,_args)
        results =  self._runFunction(
            self.perforce.run_edit
            , _args
            )
        return results

    def add(self, files=None, changelist=None):
        '''
        Mark files for add and place them in a given changelist
        '''
        results =  self._runFunction(
            self.perforce.run_add
            ,files
            ,changelist)
        return results

    def delete(self, files=None, changelist=None):
        _args = []
        if changelist != None:
            _args.extend(["-c", changelist])
        _args.extend(self._toList(files))
        results = self._runFunction(
            self.perforce.run_delete
            ,_args
            )
        return results

    def opened(self,changelist=None):
        '''
        return a list of the files that are in a partiuclar changelist,
        has no files paramater so we pass directly to the changelist property
        '''
        _args = []
        if changelist != None:
            _args.exten(["-c",changelist])
        results = self._runFunction(
            self.perforce.run_opened
            ,_args
            )
        return results

    def getChangeLists(self, pending=True, user=None, client=None):
        args = []
        if pending == True:
            args.extend(["-s", "pending"])
        if user == None:
            user = self.user
        args.extend(["-u", user])
        if client == None:
            client = self.client
        args.extend(["-c", client])
        results = self._tryFunction(
            self.perforce.run_changes
            ,*args
            )
        return results

    def _deleteChangeList(self, changelist):
        results = self._runFunction(self.perforce.delete_change,changelist)
        return results

    def deleteChangeLists(self, changelists):
        results = []
        listChangeLists = self._toList(changelists)
        openChangeLists = self.getChangeLists()
        validChangeLists = []
        for changelist in listChangeLists:
            if changelist in openChangeLists:
                results.append(self._deleteChangeList(changelist))
        return results

    def createChangeList(self, description = None, files = None, changeform = None):
        '''
        creates a changelist and returns its number
        if files are in the default changelist they will be moved to the new changelist,
            files not in the default changelist will not be moved, 
            this should be changed for transparency in functionality
        a description needs to be passed in, the AUTO default description does not provide enough 
            archival information to be useful with looking at p4 object history.
        '''
        changelist = None
        if changeform == None:
            changeform = self._tryFunction(self.perforce.fetch_change)
        if description == None:
            changeform["Description"] = "AUTO: No description passed in by {0}".format(self.user)
        else:
            changeform["Description"] = description
        if files != None:
            changeform["Files"] = self._toList(files)
        changelist = self._tryFunction(
            self.perforce.save_change
            , changeform
            )
        if changelist == None:
            # If the changelist is not created this tends to cause massive fallout down stream so throw an exception
            raise(P4Exception(
                "No change list created given changeform: \n {0}\n"\
                .format(changeform)
                )
            )
        changelistNumber = int(changelist[0].split(" ")[1])
        return changelistNumber
    
    def getChangeLists(self,user = None):
        '''
        Return the changelist numbers the user has open
        defaults to the current user can be set to other users
        '''
        if user == None:
            user = self.user
        args = ["-u", user]
        changelists = self._runFunction(self.perforce.run_changes,args)
        changes = []
        for changelist in changelists:
            # casting to int because these should all be numbers and it allows comparison in other functions
            changes.append(int(changelist["change"]))
        return changes    

    def moveToChangeList(self, changelist, files):
        '''
        move the files to an existing change list, 
        the destination changelist must already exist 
        TODO: if the destination changelist does not exist create a changelist 
            and return that changelist number.
        '''
        files = self._toList(files)
        results = self._runFunction(self.perforce.run_reopen, changelist, files)
        return results

    def updateChangelist(self, changelist, attr, value):
        '''
        Change any of the properties on an active change list using the change form.
        '''
        changeform = self._runFunction(self.perforce.fetch_change, changelist)
        changeform[attr] = value
        changelist = self._runFunction(self.perforce.save_change,changelist)
        changelistNumber = changelist[0].split(" ")[1]
        return int(changelistNumber)

    def update(self,files = None, force = False, preview = False, *args):
        '''
        update given files,
        needs a test and a version that works on directories
        '''
        _args = []
        _args.extend(args)
        if force == True:
            #slow, forces a sync on all un opened files in the client
            args = self._extendList("-f", _args)
        if preview == True:
            #the preview will print as an error this is a design issue
            args = self._extendList("-n",_args)
        if files != None:
            files = self._toList(files)
        results = self._runFunction(
            self.perforce.run_sync
            , args, files
            )
        return results

    def filesStatus(self,files):
        '''
        get perforce information about the files (or wildcard files)
        this can make use of the __initStatusDict data structure to store the data
        returns [{statusName: state, statusName: state},{statusName: state}]
        '''
        results = self._runFunction(
            self.perforce.run_fstat
            , files
            )
        return results

    def revert(self, files=None , changelist=None):
        ''' 
        Revert any changes made to files, or in a given change list
        '''
        return self._runFunction(self.perforce.run_revert,files,changelist)        


    def submit(self, description = None, files = None, changelist = None, submitOption = None):
        '''
        Submit the files using an 
        '''
        """
         SubmitOptions:  Flags to change submit behaviour.

         submitunchanged     All open files are submitted (default).

         revertunchanged     Files that have content or type changes
                             are submitted. Unchanged files are
                             reverted.

         leaveunchanged      Files that have content or type changes
                             are submitted. Unchanged files are moved
                             to the default changelist.

                 +reopen     Can be appended to the submit option flag
                             to cause submitted files to be reopened in
                             the default changelist.
                             Example: submitunchanged+reopen
        """
        submitOptions = [
            'submitunchanged'
            , 'revertunchanged'
            , 'leaveunchanged'
            , 'submitunchanged+reopen'
            , 'revertunchanged+reopen'
            , 'leaveunchanged+reopen'
            ]
        _args = []
        if submitOption != None:
            if submitOption in submitOptions:
                _args.extend(["-f", submitOption])
        if changelist not in self.getChangeLists():
            # if changelist does not exist create a changelist to use.
            # this may cause silent failure when attempting to submit files outside the default cl
            # May be a good place for an assertion in rev.2
            changelist = self.createChangeList(description = description)
        if files != None:
            self.moveToChangeList(changelist = changelist, files = files)
        _args.extend(["-c", changelist])
        results = self._runFunction(self.perforce.run_submit, _args)
        return results

    def submitChangelist(self, changelist = None):
        '''
        Submit the changelist given a single changelist number
        This is a simple submit for an entire changelist with no questions asked
        '''
        result = None
        if changelist is not None:
            openChangeLists = self.getChangeLists()
            if changelist in openChangeLists:
                _args = ["-c", changelist]
                result = self._runFunction(self.perforce.run_submit,_args)
        return result

    '''
    The following functions are intended to only work on a single file at a time
    for multiple files use the areFunctionName set.
    '''
    def isInDepot(self, filePath):
        '''
        returns true if any of the paths are in perforce
        '''
        status = self.filesStatus(filePath)
        if status != None:
            return True
        return False 

    def _isStatus (self, state, filePath, key = "action"):
        status = self.filesStatus(filePath)[0]
        if status != None:
            if key in status:
                if state != None and status[0][key] == state :
                    return True
                else:
                    return False
                return True
        return False

    def isCheckedOut(self, filePath):
        '''
        check if the file is checked out by any user from perforce, 
        '''
        if self.isCheckedOutBy(filePath) or self._isStatus(None, filePath):
            return True
        return False

    def isCheckedOutByOther(self, filePath):
        '''
        check if any other user has the file checked
        '''
        if self.isCheckedOutBy(filePath):
            return True
        return False

    def isCheckedOutBySelf(self, filePath):
        '''
        check if the currect user has the file checked out
        '''
        if self._isStatus(None, filePath):
            return True
        return False

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

    def isOpenForAdd(self, filePath):
        return self._isStatus("add", filePath)

    def isOpenForEdit(self, filePath):
        return self._isStatus("edit", filePath)

    def isEditable(seld, filePath):
        if self.isOpenForAdd(filePath) or self.isOpenForEdit(filePath):
            return True
        return False

    def isOpenForDelete(self, filePath):
        return self._isStatus("delete", filePath)

    def isLatest(self, filePath):        
        status = self.filesStatus(filePath)[0]
        if "headRev" in status and "haveRev" in status:
            if status["haveRev"] == status["headRev"]:
                return True
        return False

    def isLocked(self, filePath):
        '''
        rteturns true if the file is not marked for edit, or add
        '''
        return self._isStatus(filePath)
    
    '''
    The Are functions are intended to be used for multiple items at once
    '''

    def _areStatus(self, state, filePaths, key = "action"):
        '''
        uses the single file functions to check status on each file path
        '''
        if type(filePaths) != type(str()):
            status = self.filesStatus(filePaths)
            outStatus = {}
            for fileStatus in status:
                outIndex = fileStatus["clientFile"]
                if key in fileStatus:
                    if fileStatus[key] == state:
                        outStatus.update({outIndex: True})
                    else:
                        outStatus.update({outIndex: False})
                    outStatus.update({outIndex: True})
                else:
                    outStatus.update({outIndex: False})
            return outStatus
        elif type(filePaths) == type(str()):
            return self._isStatus(state, filePaths, key)
        return None

    def areCheckedOut(self, filePaths):
        '''
        compantion to the isCheckedOut function 
        intended to check is multiple files are checked out
        [filePath,filePath -> [bool, bool]
        '''
        return self._areStatus(None,filePaths)

    def areCheckedOutBy(self, filePaths):
        '''
        returns a dictionary of fileName:status
        '''
        outStatuses = {}
        statuses = self.filesStatus(filePaths)
        for index,status in enumerate(statuses):
            otherNames = [] # a list of all the other uses with the file checked out.
            if "otherOpen" in status:    
                for name in status["otherOpen"]:
                    name = name.split("@")[0].split(".")
                    nameOut = name[0][0].upper() + name[0][1:].lower() + " " +\
                        name[1][0].upper() + name[1][1:].lower()
                    otherNames.append(nameOut)
                outStatuses.update({filePaths[index]:otherNames})
            else:
                outStatuses.update({filePaths[index]:False})
        return outStatuses

    def areOpenForAdd(self, filePaths):
        return self._areStatus("add",filePaths)

    def areOpenForEdit(self, filePaths):
        return self._areStatus("edit", filePaths)

    def areEditable(self, filePaths):
        editable = self._areStatus("edit",filePaths)
        added  = self._areStatus("add",filePaths)
        outStatus = {}
        for key in editable:
            if editable[key] ==True or added[key] == True:
                outStatus[key] = True

    def areOpenForDelete(self, filePaths):
        return self._areStatus("delete",filePaths)

    def areLatest(self, filePaths):
        inWorkspace =  self.filesStatus(filePaths)
        outStatus = {}
        for status in inWorkspace:
            if ("headRev" in status) and ("heaveRev" in status):
                if status["headRev"] == status["haveRev"]:
                    outStatus[status[clientFile]] = True
            outStatus[status["clientFile"]] = False

    def areLocked(self, filePaths):
        return self._areStatus(None, filePaths)

if __name__ == '__main__':
    # when executing the file run its tests to verify that the functions work
    import perforce.p4Console_TestRunner
    
