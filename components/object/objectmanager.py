class ObjectManager:
    def __init__(self, renderer):
        # items are key:value -> list_name:list_of_objects
        self.item_dict = {}
        # main domain group, everything in this group will be drawn onscreen
        # 'domain' is a reserved list name, it is all the objects that will be drawn
        from components.bundled.pyscroll.group import PyscrollGroup
        self.item_dict['domain'] = PyscrollGroup(renderer)

    def object_add(self, name, object):
        # append and add an object to the named list and the domain group
        if name not in self.item_dict.keys():
            self.item_dict[name] = []
        self.item_dict[name].append(object)
        self.domain_add(object)

    def object_remove(self, name, object):
        # remove an object from the named list
        if name in self.item_dict.keys():
            self.item_dict[name].remove(object)

    def objects(self, name):
        # return all the objects for a name as a list
        if name in self.item_dict.keys():
            return self.item_dict[name]
        else:
            return []

    def domain_add(self, object):
        # add an object into the domain group only
        self.item_dict['domain'].add(object)

    def domain_remove(self, object):
        # remove an object from the domain group
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
                self.domain_remove(object)
