# -*- coding: utf-8 -*-
##
## $Id: mail.py,v 1.8 2009/04/15 15:17:45 dmartinc Exp $
##
## This file is par{t of CDS Indico.
## Copyright (C) 2002, 2003, 2004, 2005, 2006, 2007 CERN.
##
## CDS Indico is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## CDS Indico is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with CDS Indico; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
from MaKaC.webinterface.mail import GenericNotification

from MaKaC.common.info import HelperMaKaCInfo
from MaKaC.plugins.Collaboration.collaborationTools import CollaborationTools
from MaKaC.plugins.Collaboration.RecordingRequest.common import typeOfEvents,\
    postingUrgency, recordingPurpose, intendedAudience, subjectMatter, lectureOptions
from MaKaC.webinterface import urlHandlers
from MaKaC.common.utils import formatDateTime
from MaKaC.common.timezoneUtils import getAdjustedDate
from MaKaC.plugins.base import PluginsHolder

def needToSendEmails():
    recordingRequest = PluginsHolder().getPluginType('Collaboration').getPlugin('RecordingRequest')
    
    admins = recordingRequest.getOption('admins').getValue()
    sendMailNotifications = recordingRequest.getOption('sendMailNotifications').getValue()
    additionalEmails = recordingRequest.getOption('additionalEmails').getValue()
    
    return (sendMailNotifications and len(admins) > 0) or len(additionalEmails) > 0

class RecordingRequestNotificationBase(GenericNotification):
    """ Base class to build an email notification for the Recording request plugin.
    """
    def __init__(self, booking):
        GenericNotification.__init__(self)
        
        self._booking = booking
        self._bp = booking._bookingParams
        self._conference = booking.getConference()
        
        adminEmails = [u.getEmail() for u in booking.getPluginOptionByName('admins').getValue()]
        additionalEmails = booking.getPluginOptionByName("additionalEmails").getValue()
        
        self._displayLink = urlHandlers.UHConferenceDisplay.getURL(self._conference)
        self._adminLink = urlHandlers.UHConfModifCollaboration.getURL(self._conference,
                                                                      secure = CollaborationTools.isUsingHTTPS(),
                                                                      tab = CollaborationTools.getPluginSubTab(booking.getPlugin()))
        
        self.setFromAddr("Indico Mailer<%s>"%HelperMaKaCInfo.getMaKaCInfoInstance().getSupportEmail())
        self.setToList(adminEmails + additionalEmails)
        self.setContentType("text/html")
        
    def _getEventDetails(self):
        return """
Event details:
<table style="border-spacing: 10px 10px;">
    <tr>
        <td style="vertical-align: top; white-space : nowrap;">
            <strong>Event name:</strong>
        </td>
        <td>
            %s <a href="%s">(link)</a>
        </td
    </tr>
    <tr>
        <td style="vertical-align: top; white-space : nowrap;">
            <strong>Event id</strong>
        </td>
        <td>
            %s
        </td
    </tr>
</table>
"""%(self._conference.getTitle(),
     self._displayLink,
     self._conference.getId()
     )

    def _getOrganizerDetails(self):
        creator = self._conference.getCreator()
        
        additionalEmailsText = ""
        additionalEmails = creator.getSecondaryEmails()
        if additionalEmails:
            additionalEmailsText="""
    <tr>
        <td style="vertical-align: top; white-space : nowrap;">
            <strong>Additional emails:</strong>
        </td>
        <td>
            %s
        </td
    </tr>
""" % ", ".join(creator.getEmails()[1:])

        additionalTelephonesText = ""
        additionalTelephones = creator.getSecondaryTelephones()
        if additionalTelephones:
            additionalTelephonesText="""
    <tr>
        <td style="vertical-align: top; white-space : nowrap;">
            <strong>Additional telephones:</strong>
        </td>
        <td>
            %s
        </td
    </tr>
""" % ", ".join(creator.getTelephone()[1:])

        
        return """
Creator of the event details:
<table style="border-spacing: 10px 10px;">
    <tr>
        <td style="vertical-align: top; white-space : nowrap;">
            <strong>Full name:</strong>
        </td>
        <td>
            %s
        </td
    </tr>
    <tr>
        <td style="vertical-align: top; white-space : nowrap;">
            <strong>Main email address:</strong>
        </td>
        <td>
            %s
        </td
    </tr>
    %s
    <tr>
        <td style="vertical-align: top; white-space : nowrap;">
            <strong>Main phone number:</strong>
        </td>
        <td>
            %s
        </td
    </tr>
    %s
</table>
""" % (creator.getFullName(),
       creator.getEmail(),
       additionalEmailsText,
       creator.getTelephone(),
       additionalTelephonesText
       )
    
    def _getCreationDate(self):
        return formatDateTime(getAdjustedDate(self._booking.getCreationDate(), self._conference))
    
    def _getModificationDateRow(self, typeOfMail):
        if (typeOfMail == 'new'):
            return ""
        else:
            return """
    <tr>
        <td style="vertical-align: top; white-space : nowrap;">
            <strong>Modification date:</strong>
        </td>
        <td style="vertical-align: top;">
            %s
        </td>
    </tr>
""" % formatDateTime(getAdjustedDate(self._booking.getModificationDate(), self._conference))

        
    def _getRequestDetails(self, typeOfMail):
        bp = self._bp
        
        return """
Request details:<br />
<table style="border-spacing: 10px 10px;">
    <tr>
        <td style="vertical-align: top; white-space : nowrap;">
            <strong>Request id:</strong>
        </td>
        <td style="vertical-align: top;">
            %s
        </td>
    </tr>
    <tr>
        <td style="vertical-align: top; white-space : nowrap;">
            <strong>Creation date:</strong>
        </td>
        <td style="vertical-align: top;">
            %s
        </td>
    </tr>
    %s
    <tr>
        <td style="vertical-align: top; white-space : nowrap;">
            <strong>Talk(s) to be recorded:</strong>
        </td>
        <td style="vertical-align: top;">
            %s
        </td>
    </tr>
    <tr>
        <td colspan="2">
            <strong>Comments about talk selection</strong><br />
            %s
        </td>
    </tr>
    <tr>
        <td colspan="2">
            <strong>Have all the speakers given permission to have their talks recorded?</strong>  %s
        </td>
    </tr>
    <tr>
        <td style="vertical-align: top; white-space : nowrap;">
            <strong>Lecture options:</strong>
        </td>
        <td style="vertical-align: top">
            %s
        </td>
    </tr>
    <tr>
        <td style="vertical-align: top; white-space : nowrap;">
            <strong>Type of event:</strong>
        </td>
        <td style="vertical-align: top">
            %s
        </td>
    </tr>
    <tr>
        <td style="vertical-align: top; white-space : nowrap;">
            <strong>Posting urgency:</strong>
        </td>
        <td style="vertical-align: top">
            %s
        </td>
    </tr>
    <tr>
        <td style="vertical-align: top; white-space : nowrap;">
            <strong>Number of remote viewers:</strong>
        </td>
        <td style="vertical-align: top">
            %s
        </td>
    </tr>
    <tr>
        <td style="vertical-align: top; white-space : nowrap;">
            <strong>Number of attendees:</strong>
        </td>
        <td style="vertical-align: top">
            %s
        </td>
    </tr>
    <tr>
        <td style="vertical-align: top; white-space : nowrap;">
            <strong>Recording purpose(s):</strong>
        </td>
        <td style="vertical-align: top">
            %s
        </td>
    </tr>
    <tr>
        <td style="vertical-align: top; white-space : nowrap;">
            <strong>Intended audience(s):</strong>
        </td>
        <td style="vertical-align: top; white-space : nowrap;">
            %s
        </td>
    </tr>
    <tr>
        <td style="vertical-align: top; white-space : nowrap;">
            <strong>Subject matter(s):</strong>
        </td>
        <td style="vertical-align: top">
            %s
        </td>
    </tr>
    <tr>
        <td colspan="2">
            <strong>Additional comments:</strong><br />
            %s
        </td>
    </tr>
</table>
"""%(self._booking.getId(),
     self._getCreationDate(),
     self._getModificationDateRow(typeOfMail),
     self._getTalks(),
     self._getTalkSelectionComments(),
     bp["permission"],
     dict(lectureOptions)[bp["lectureOptions"]],
     dict(typeOfEvents)[bp['lectureStyle']],
     dict(postingUrgency)[bp['postingUrgency']],
     bp['numRemoteViewers'],
     bp['numAttendees'],
     self._getPurposes(),
     self._getAudiences(),
     self._getMatters(),
     self._getComments()
     )
        
    def _getTalks(self):
        #"all" "choose" "neither"
        if self._bp["talks"] == "all":
            return """All talks"""
        elif self._bp["talks"] == "neither":
            return """Please see the talk selection comments"""
        else:
            text = ["""The user chose the following talks:"""]
            
            for contributionId in self._bp["talkSelection"]:
                conf = self._booking.getConference()
                contribution = conf.getContributionById(contributionId)
                
                speakerList = contribution.getSpeakerList()
                if speakerList:
                    speakers = ', by ' + ", ".join([person.getFullName() for person in speakerList])
                else:
                    speakers = ''
                    
                if contribution.getLocation():
                    locationText = "Location: " + contribution.getLocation().getName()
                    if contribution.getRoom():
                        locationText += ', Room: ' + contribution.getRoom().getName()
                    else:
                        locationText += ', Room: not defined'
                else:
                    locationText = "Location: not defined"
                    
                contributionLine = """•[%s] <a href="%s">%s</a>%s (%s)""" % (
                    contributionId,
                    urlHandlers.UHContributionDisplay.getURL(contribution),
                    contribution.getTitle(),
                    speakers,
                    locationText
                )
                text.append(contributionLine)
            
            return "<br />".join(text)
                
                
        
    def _getTalkSelectionComments(self):
        comments = self._bp["talkSelectionComments"].strip()
        if comments:
            return comments
        return "(User didn't write any comments)"
    
    def _getComments(self):
        comments = self._bp["otherComments"].strip()
        if comments:
            return comments
        return "(User didn't write any comments)"
        
    @classmethod
    def listToStr(cls, list):
        return "<br />".join([("•" + item) for item in list]) 
        
    def _getLectureOptions(self):
        options = self._bp['lectureOptions']
        lodict = dict(lectureOptions)
        if options:
            return RecordingRequestNotificationBase.listToStr([lodict[k] for k in options])
        else:
            return "No lecture options were selected"
        
    def _getPurposes(self):
        purposes = self._bp['recordingPurpose']
        rpdict = dict(recordingPurpose)
        if purposes:
            return RecordingRequestNotificationBase.listToStr([rpdict[k] for k in purposes])
        else:
            return "No purposes were selected"
        
    def _getAudiences(self):
        audiences = self._bp['intendedAudience']
        iadict = dict(intendedAudience)
        if audiences:
            return RecordingRequestNotificationBase.listToStr([iadict[k] for k in audiences])
        else:
            return "No audiences were selected"
        
    def _getMatters(self):
        matters = self._bp['subjectMatter']
        smdict = dict(subjectMatter)
        if matters:
            return RecordingRequestNotificationBase.listToStr([smdict[k] for k in matters])
        else:
            return "No audiences were selected"




class NewRequestNotification(RecordingRequestNotificationBase):
    """ Template to build an email notification to the recording responsible
    """
    
    def __init__(self, booking):
        RecordingRequestNotificationBase.__init__(self, booking)
        
        self.setSubject("""[Indico] [New recording request] %s (event id: %s)"""
                        % (self._conference.getTitle(), str(self._conference.getId())))
        
        self.setBody("""Dear Recording Responsible,<br />
<br />
There is a <strong>new recording request</strong>.<br />
Click <a href="%s">here</a> to accept or reject the request.<br />
<br />
%s
<br />
%s
<br />
You also can see a list of all the requests here: (not implemented yet).<br />
<br />
<br />
%s
""" % ( self._adminLink,
        self._getEventDetails(),
        self._getOrganizerDetails(),
        self._getRequestDetails('new')
        ))
        
        
        
class RequestModifiedNotification(RecordingRequestNotificationBase):
    """ Template to build an email notification to the recording responsible
    """
    
    def __init__(self, booking):
        RecordingRequestNotificationBase.__init__(self, booking)
        
        self.setSubject("""[Indico] [Recording request modified] %s (event id: %s)"""
                        % (self._conference.getTitle(), str(self._conference.getId())))
        
        self.setBody("""Dear Recording Responsible,<br />
<br />
A recording request <strong>was modified</strong>.<br />
Click <a href="%s">here</a> to accept or reject the request.<br />
<br />
%s
<br />
%s
<br />
You also can see a list of all the requests here: (not implemented yet).<br />
<br />
<br />
%s
""" % ( self._adminLink,
        self._getEventDetails(),
        self._getOrganizerDetails(),
        self._getRequestDetails('modify')
        ))
        
        
        
class RequestDeletedNotification(RecordingRequestNotificationBase):
    """ Template to build an email notification to the recording responsible
    """
    
    def __init__(self, booking):
        RecordingRequestNotificationBase.__init__(self, booking)
        
        self.setSubject("""[Indico] [Recording request deleted] %s (event id: %s)"""
                        % (self._conference.getTitle(), str(self._conference.getId())))
        
        self.setBody("""Dear Recording Responsible,<br />
<br />
A recording request <strong>was withdrawn</strong>.<br />
<br />
%s
<br />
%s
<br />
You also can see a list of all the requests here: (not implemented yet).<br />
<br />
<br />
%s
""" % ( self._getEventDetails(),
        self._getOrganizerDetails(),
        self._getRequestDetails('remove')
        ))