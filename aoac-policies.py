## python 2.7 ##

## BELL-LAPADULA POLICY MODEL ##

class CO: # i.e. the class of Classification Object
    class_order = ["unclassified", "classified", "secret", "top_secret"]
    def __init__(self, name, classification):
        self.name = name
        self.classification = classification
    def get_classification(self):
        return self.classification

class BLPUser(CO): ## i.e. agents
    def __init__(self, name, classification):
        CO.__init__(self, name, classification)

    def read(self, asset):
        if isinstance(asset, BLPAsset):
            return asset.get_message(self)

    def write(self, asset, new_message):
        if isinstance(asset, BLPAsset):
            return asset.set_message(self, new_message)

        
class BLPAsset(CO): ## i.e. resources
    def __init__(self, name, message, classification):
        CO.__init__(self, name, classification)
        self.message = message

    def get_message(self, user): ## no read up
        if isinstance(user, BLPUser):
            if self.class_order.index((user.classification)) >= self.class_order.index(self.classification):
                return self.message
        return "Unable to read."
 
    def set_message(self, user, new_message): ## no write down
        if isinstance(user, BLPUser):
            if self.class_order.index((user.classification)) <= self.class_order.index(self.classification):
                self.message = new_message
                return self.message
        return "Unable to write."

ts = BLPUser("Tanya", "top_secret")
s = BLPUser("Sarah", "secret")
c = BLPUser("Charles", "classified")
u = BLPUser("Ulysses", "unclassified")

tsa = BLPAsset("top_secret_asset", "This is a top secret message.", "top_secret")
sa = BLPAsset("secret_asset", "This is a secret message.", "secret")
ca = BLPAsset("classified asset", "This is a classified message.", "classified")
ua = BLPAsset("unclassified asset", "This is an unclassified message.", "unclassified")

print "Example 1: secret agent unable to read up"
print s.read(tsa)
print s.read(sa)
print s.read(ca)
print s.read(ua)

print "Example 2: top secret agent unable to write down"
print ts.write(tsa, "I can write here.")
print ts.write(sa, "I can write here.")
print ts.write(ca, "I can write here.")
print ts.write(ua, "I can write here.")

## CLARK-WILSON POLICY MODEL ##

class CWAsset:
    the_log = []
    # note this is at the level of the system, as per the Clark-Wilson paper (p190)

    def __init__(self, name, user_tp_pairs, certification_users):
        self.name = name
        self.user_tp_pairs = user_tp_pairs
        self.certification_users = certification_users

    def execute(self, user, tp):
        if user in self.certification_users:
            return "User cannot execute a CDI it certifies."
        if (user, tp) in self.user_tp_pairs:
            self.the_log.append([self, user, "exe"])
            return user + " executes " + tp + " on " + self.name
        
    def modify_user_tp_pairs(self, user, new_tp_pairs):
        if user in self.certification_users:
            if user in [pairs[0] for pairs in self.user_tp_pairs]:
                return "Execution user cannot certify this CDI."
        else:
            return "User does not have certification rights on this CDI."
        self.the_log.append([self, user, "exe"])
        self.user_tp_pairs = new_tp_pairs
        return


print "Example 1: User John executes some trusted process (tp_1) on an asset."

cwasset = CWAsset("cwasset", [("john", "tp_1"), ("mary", "tp_1")], ["mary", "sysad_1"])
print cwasset.execute("john", "tp_1")

print "Example 2: Mary cannot do the same (separation of duty requirement)"
print cwasset.execute("mary", "tp_1")

print "Example 3: John cannot certify the asset. The log stores all previous executions."
print cwasset.modify_user_tp_pairs("john", [["mary", "tp_2"]])
print cwasset.the_log


## LAISSEZ-FAIRE POLICY MODEL ##
class LFAsset:
    def __init__(self, name, message, owner, rights):
        self.name = name
        self.message = message
        self.owner = owner
        self.rights = rights
        self.history = []
        self.basic_history = []
        
    def read(self, user):
        if user in self.rights[0]:
            self.add_to_history()
            self.basic_history.append([user, "read"])
            return self.message
        return "User does not have read-permission."
    
    def write(self, user, new_message):
        if user in self.rights[1]:
            self.add_to_history()
            self.basic_history.append([user, "write"])
            self.message = new_message
            return
        return "User does not have write-permission."

    def modify_rights(self, owner, new_rights):
        if owner == self.owner:
            self.add_to_history()
            self.basic_history.append([owner, "modify_rights"])
            self.rights = rights
            return
        return "User must be owner to modify rights."
    
    def delegation(self, owner, new_owner): # freedom of delegation requirement
        if owner == self.owner:
            self.add_to_history()
            self.basic_history.append([owner, "delegate_ownership"])
            self.owner = new_owner
            return
        return "User must be owner to delegate rights."

    def add_to_history(self): # full transparency requirement
        self.history.append(self)

    def give_basic_history(self, user):
        self.add_to_history()
        self.basic_history.append([user, "give_basic_history"])
        return self.basic_history
    
##rights of the form: read rights, write rights, history
print "------------------"
print "Example 1: Alice creates an asset and gives Bob read-access. They both try to write to it"

a = LFAsset("asset_a", "This is Alice's asset.", "Alice", [["Alice", "Bob"],["Alice"]])
print a.read("Bob")
print a.write("Bob", "Can I write to this file?")
a.write("Alice", "This is a new message written by Alice.")

print "Example 2: As per `transparency', Bob (and any user) can see any changes."
a.give_basic_history("Bob")

print "Laissez-Faire Example 3: Alice delegates ownership to Bob"
a.delegation("Alice", "Bob")
