from components.bundled.pyscroll.group import PyscrollGroup

class ObjectManager:
    def __init__(self, renderer):
        self.item_dict = dict()
        # main domain list
        self.item_dict['domain'] = PyscrollGroup(renderer)

    def add(self, name, object):
        if not (name in self.item_dict.keys()):
            self.item_dict[name] = []
        self.item_dict[name].append(object)
        self.domain_put(object)

    def objects(self, name):
        if name in self.item_dict.keys():
            return self.item_dict[name]
        else:
            return []

    def item_pop(self, name, object):
        if name in self.item_dict.keys():
            self.item_dict[name].remove(object)

    def transfer(self, name1, name2, object):
        if not (name1 in self.item_dict.keys()):
            raise('no source item list')
        if not (name2 in self.item_dict.keys()):
            # create new destination list
            self.item_dict[name2] = []
        if object in self.item_dict[name1]:
            self.item_dict[name1].remove(object)
            self.item_dict[name2].append(object)

    def domain_put(self, object):
        self.item_dict['domain'].add(object)

    def domain_pop(self, object):
        if object in self.item_dict['domain']:
            self.item_dict['domain'].remove(object)

    def domain(self):
        return self.item_dict['domain']

    def delete(self, name, object):
        if name in self.item_dict.keys():
            if object in self.item_dict[name]:
                self.item_dict[name].remove(object)
            if object in self.domain():
                self.domain_pop(object)
