import core

link = 'https://www.youtube.com/playlist?list=PLbyorRThEk_LczvBPiBDNaejrjGQILDTO'
folder = './download/PLbyorRThEk_LczvBPiBDNaejrjGQILDTO'
video = core.Video(link, folder)
video.searchCatalog(query=None)
video.saveCatalog()