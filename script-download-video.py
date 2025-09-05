import core
import foundation

link = 'https://www.youtube.com/playlist?list=PLf5hP3QpCpY5VYN0AJQrELWxgUJUIV3yw'
storage = './download/Share-a-short-video-every-day'
# query = None
site = core.Site(storage)
site.searchPlaylist(link)
site.savePlaylist()
archive = site.getArchive()
# iteration = archive
# for source in iteration:
#     site.saveVideo(source)
#     continue
# _ = iteration

operation = foundation.Operation(core=2)
operation.activatePipeline(
    archive, site.downloadVideo, {}
)

# site.downloadVideo()