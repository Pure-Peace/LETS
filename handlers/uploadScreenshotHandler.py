import glob
from constants import exceptions
from helpers import generalHelper
from helpers import requestHelper
import os
from helpers import logHelper as log
from helpers.exceptionsTracker import trackExceptions
from helpers import userHelper

# Exception tracking
import tornado.web
import tornado.gen
import sys
import traceback
from raven.contrib.tornado import SentryMixin

MODULE_NAME = "screenshot"
class handler(SentryMixin, requestHelper.asyncRequestHandler):
	"""
	Handler for /web/osu-screenshot.php
	"""
	@tornado.web.asynchronous
	@tornado.gen.engine
	def asyncPost(self):
		try:
			if glob.debug == True:
				requestHelper.printArguments(self)

			# Make sure screenshot file was passed
			if "ss" not in self.request.files:
				raise exceptions.invalidArgumentsException(MODULE_NAME)

			# Check user auth because of sneaky people
			if not requestHelper.checkArguments(self.request.arguments, ["u", "p"]):
				raise exceptions.invalidArgumentsException(MODULE_NAME)
			username = self.get_argument("u")
			password = self.get_argument("p")
			userID = userHelper.getID(username)
			if not userHelper.checkLogin(userID, password):
				raise exceptions.loginFailedException(MODULE_NAME, username)

			# Get a random screenshot id
			found = False
			while found == False:
				screenshotID = generalHelper.randomString(8)
				if os.path.isfile(".data/screenshots/{}.jpg".format(screenshotID)) == False:
					found = True

			# Write screenshot file to .data folder
			with open(".data/screenshots/{}.jpg".format(screenshotID), "wb") as f:
				f.write(self.request.files["ss"][0]["body"])

			# Output
			log.info("New screenshot ({})".format(screenshotID))

			# Return screenshot link
			self.write("{}/ss/{}.jpg".format(glob.conf.config["server"]["serverurl"], screenshotID))
		except exceptions.invalidArgumentsException:
			pass
		except exceptions.loginFailedException:
			pass
		except:
			log.error("Unknown error in {}!\n```{}\n{}```".format(MODULE_NAME, sys.exc_info(), traceback.format_exc()))
			if glob.sentry:
				yield tornado.gen.Task(self.captureException, exc_info=True)
		#finally:
		#	self.finish()
