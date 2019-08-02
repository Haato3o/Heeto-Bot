from requests import request
from bs4 import BeautifulSoup

class Servers():
    SLS = {
        "na" : "http://sls.service.enmasse.com:8080/servers/list.en",
        "eu" : "http://web-sls.tera.gameforge.com:4566/servers/list.uk",
        "ru" : "http://launcher.tera-online.ru/launcher/sls/",
        "tw" : "http://tera.mangot5.com/game/tera/serverList.xml"
    }

    @staticmethod
    def GetTeraStatus(region: str) -> dict:
        '''
            Get and return current status of servers
            :param region: Region name
            :return: dict
        '''
        Status = {}
        RegionSLS = Servers.SLS.get(region)
        if RegionSLS != None:
            SLSResponse = request('GET', RegionSLS).text
            bs = BeautifulSoup(SLSResponse, 'html.parser')
            serverNames = bs.find_all('name')
            serverStatus = bs.find_all('permission_mask')

            for name in serverNames:
                Status[name['raw_name'].strip('\n')] = None
            for status in range(len(serverStatus)):
                Status[serverNames[status]['raw_name'].strip('\n')] = 'up' if serverStatus[status].get_text() == "0x00000000" else 'down'
        return Status