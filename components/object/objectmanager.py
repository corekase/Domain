from components.bundled.pyscroll.group import PyscrollGroup

class ObjectManager:
    def __init__(self, renderer):
        # items are key:value -> list_name:list_of_objects
        self.item_dict = dict()
        # main domain group, everything in this group will be drawn onscreen
        self.item_dict['domain'] = PyscrollGroup(renderer)

    def add(self, name, object):
        # append an object to the list called name
        if not (name in self.item_dict.keys()):
            self.item_dict[name] = []
        self.item_dict[name].append(object)
        self.domain_put(object)

    def objects(self, name):
        # return all the objects for a name as a list
        if name in self.item_dict.keys():
            return self.item_dict[name]
        else:
            return []

    def item_pop(self, name, object):
        # remove an object from the named list
        if name in self.item_dict.keys():
            self.item_dict[name].remove(object)

    def domain_put(self, object):
        # put an object into the domain group only
        self.item_dict['domain'].add(object)

    def domain_pop(self, object):
        # pop an object from the domain group
        if object in self.item_dict['domain']:
            self.item_dict['domain'].remove(object)

    def domain(self):
        # return the domain group
        return self.item_dict['domain']

    def delete(self, name, object):
        # remove an object from both its named list and the domain group
        if name in self.item_dict.keys():
            if object in self.item_dict[name]:
                self.item_dict[name].remove(object)
            if object in self.domain():
                self.domain_pop(object)
