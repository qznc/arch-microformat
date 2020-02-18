#!/usr/bin/env python3

import sys
import xml.etree.ElementTree as ET

class Parser:
    def __init__(self):
        self.nodes = dict()
        self.relations = dict()
        self.current_id = 0
        self.current_node = None
        self.current_relation = None
    def new_id(self):
        self.current_id += 1
        return self.current_id
    def parse_tag(self, elem):
        classes = elem.attrib.get('class', '').split()
        if 'arc-node' in classes:
            self.parse_node(elem)
        elif 'arc-relation' in classes:
            self.parse_relation(elem)
        else:
            for c in classes:
                txt = elem.text.strip()
                if self.current_node and not c in self.current_node:
                    self.current_node[c] = txt
                if self.current_relation and c == 'target':
                    self.current_relation['target'].add(txt)
                elif self.current_relation and not c in self.current_relation:
                    self.current_relation[c] = txt
            for child in elem:
                self.parse_tag(child)
    def parse_node(self, elem):
        prev_node = self.current_node
        self.current_node = dict()
        id = elem.attrib.get('id', None) or self.new_id()
        assert not id in self.nodes
        self.current_node['id'] = id
        for child in elem:
            self.parse_tag(child)
        self.nodes[id] = self.current_node
        self.current_node = prev_node
    def parse_relation(self, elem):
        prev_relation = self.current_relation
        self.current_relation = dict()
        id = elem.attrib.get('id', None) or self.new_id()
        assert not id in self.relations
        self.current_relation['id'] = id
        self.current_relation['source'] = set()
        self.current_relation['target'] = set()
        if self.current_node:
            self.current_relation['source'].add(self.current_node['id'])
        for child in elem:
            self.parse_tag(child)
        self.relations[id] = self.current_relation
        self.current_relation = prev_relation

tree = ET.parse("example/index.html")
root = tree.getroot()
p = Parser()
p.parse_tag(root)
        
for id,r in p.relations.items():
    for s in r['source']:
        n = p.nodes.get(s, dict()).get('name', '')
        print(f"{n} [{s}]", end='')
    desc = r.get('description', '').replace('\n', '')
    print(f" --{desc}-> ", end='')
    for s in r['target']:
        n = p.nodes.get(s, dict()).get('name', '')
        print(f"{n} [{s}]", end='')
    print()
