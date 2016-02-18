# Copyright 2011 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
import webob.exc

from nova.api.openstack import common
from nova.api.openstack import wsgi
from nova import exception
from nova.i18n import _
from nova.compute import api as compute_api
from oslo_log import log as logging

LOG = logging.getLogger(__name__)
class Controller(wsgi.Controller):
    """Base controller for changing / viewing delete_on_termination flag."""

    def __init__(self, **kwargs):
        super(Controller, self).__init__(**kwargs)
        self._compute_api = compute_api.API()

    def view(self,volume):
        if volume is not None:
            vol_view= { "id": volume.volume_id , "instance": volume.instance_uuid, "delete_on_termination":volume.delete_on_termination }
            return vol_view
        else:
            return None
        
    def show(self, req, id):
        """Return delete_on_termination flag of a block volume.

        :param req: `wsgi.Request` object
        :param id: volume identifier """
        context = req.environ['nova.context']
        volume=None
        try:
            volume = self._compute_api.get_block_device_mapping_termination_flag(context,id )
        except (exception.NotFound):
            explanation = _("Either %s volume does not exist or is not attached to any instance"%(id))
            raise webob.exc.HTTPNotFound(explanation=explanation)
#        return self._view_builder.show(req, image)
        return self.view(volume)

    def update(self,req,body,id):
        """  updates the delete_on_termination flag as asked by used
        :param req `wsgi.Request` object
        :param id: volume identifier 
        """
        context = req.environ['nova.context']
        volume=None
        try:
            flag = False
            if 'delete_on_termination' in body:
                if body['delete_on_termination'] == "True":
                   flag=True
                elif body['delete_on_termination'] == "False":
                   flag=False
                #else raise an exception invalid value
            volume = self._compute_api.update_block_device_mapping_termination_flag(context,id,flag)
        except(exception.NotFound):
            explanation = _("Either %s volume does not exist or is not attached to any instance"%(id))
            raise webob.exc.HTTPNotFound(explanation=explanation)
        robj=wsgi.ResponseObject(self.view(volume))
        return robj
        
def create_resource():
    return wsgi.Resource(Controller())
