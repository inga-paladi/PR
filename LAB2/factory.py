import json
import xml.etree.ElementTree as ET
from io import BytesIO
from datetime import datetime
from google.protobuf.json_format import Parse, MessageToJson
from player_pb2 import PlayersList

from player import Player
from player_pb2 import Class

class PlayerFactory:
    def to_json(self, players):
        listOfJsonPlayers = []
        for player in players:
            playerJson = {
                "nickname": player.nickname,
                "email": player.email,
                "date_of_birth": str(player.date_of_birth.date()),
                "xp": player.xp,
                "class": player.cls
            }
            listOfJsonPlayers.append(playerJson)
        return listOfJsonPlayers

    def from_json(self, list_of_dict):
        return [self._create_player_from_dict(player_data) for player_data in list_of_dict]

    def from_xml(self, xml_string):
        root = ET.fromstring(xml_string)
        player_list = []
        for player_elem in root.findall('player'):
            player = Player(
                nickname=player_elem.find("nickname").text,
                email=player_elem.find("email").text,
                date_of_birth = player_elem.find("date_of_birth").text,
                xp = int(player_elem.find("xp").text),
                cls = player_elem.find("class").text    
                )
            player_list.append(player)
        return player_list

    def to_xml(self, list_of_players):
        dataTag = ET.Element('data')
        for player in list_of_players:
            playerTag = ET.SubElement(dataTag, "player")
            ET.SubElement(playerTag, "nickname").text = player.nickname
            ET.SubElement(playerTag, "email").text = player.email
            ET.SubElement(playerTag, "date_of_birth").text = str(player.date_of_birth.date())
            ET.SubElement(playerTag, "xp").text = str(player.xp)
            ET.SubElement(playerTag, "class").text = player.cls

        return ET.tostring(dataTag).decode()

    def from_protobuf(self, binary):
        players_list = PlayersList()
        players_list.ParseFromString(binary)
        player_objects = []
        for player_proto in players_list.player:
            player_data = {
                "nickname": player_proto.nickname,
                "email": player_proto.email,
                "date_of_birth": player_proto.date_of_birth,
                "xp": player_proto.xp,
                "cls": player_proto.cls,
            }
            player_objects.append(self._create_player_from_dict(player_data))
        return player_objects

    def to_protobuf(self, list_of_players):
        players_list = PlayersList()
        for player in list_of_players:
            player_proto = players_list.player.add()
            player_proto.nickname = player.nickname
            player_proto.email = player.email
            player_proto.date_of_birth = player.date_of_birth.strftime("%Y-%m-%d")
            player_proto.xp = player.xp
            player_proto.cls = player.cls
        return players_list.SerializeToString()

    def _create_player_from_dict(self, player_data):
        if 'class' in player_data:
            player_data['cls'] = player_data.pop('class')
        return Player(**player_data)