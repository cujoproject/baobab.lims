from Products.CMFCore.utils import getToolByName
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface.declarations import implements

from bika.lims.browser.bika_listing import BikaListingView
from bika.sanbi import bikaMessageFactory as _
from bika.sanbi.permissions import *


class ShipmentsView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(ShipmentsView, self).__init__(context, request)
        self.context = context
        self.request = request
        self.contentFilter = {'portal_type': 'Shipment',
                              'sort_on': 'sortable_title'}
        request.set('disable_plone.rightcolumn', 1)
        self.context_actions = {}
        self.catalog = 'bika_catalog'
        self.title = self.context.translate(_("Shipments"))
        self.icon = self.portal_url + \
                    "/++resource++bika.sanbi.images/shipment_big.png"
        self.description = ""
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = False
        self.pagesize = 50

        if self.context.portal_type == 'Shipments':
            self.request.set('disable_border', 1)

        self.columns = {
            'ShipmentID': {'title': _('Shipment ID'),
                           'index': 'sortable_title',
                           'toggle': True},
            'Project': {'title': _('Project'),
                        'toggle': True},
            'Courier': {'title': _('Courier'),
                        'toggle': True},
            'TrackingURL': {'title': _('Tracking URL'),
                            'toggle': True},
            'ShippingDate': {'title': _('Shipping Date'),
                             'toggle': True},
        }

        self.review_states = [
            {
                'id': 'default',
                'title': _('All'),
                'contentFilter': {},
                'columns': [
                    'ShipmentID',
                    'Project',
                    'Courier',
                    'TrackingURL',
                    'ShippingDate'
                ]
            },
            {
                'id': 'pending',
                'title': _('Pending'),
                'contentFilter': {'review_state': 'pending'},
                'columns': [
                    'ShipmentID',
                    'Project',
                    'Courier',
                    'TrackingURL',
                    'ShippingDate'
                ]
            },
        ]

    def __call__(self):

        mtool = getToolByName(self.context, 'portal_membership')
        if mtool.checkPermission(AddShipment, self.context) and \
                self.context.portal_type == 'Project':
            self.context_actions[_('Add')] = {
                'url': 'createObject?type_name=Shipment',
                'icon': '++resource++bika.lims.images/add.png'
            }
        if mtool.checkPermission(ManageShipments, self.context):
            stat = self.request.get("%s_review_state" % self.form_id, 'default')
            self.show_select_column = stat != 'all'
        return super(ShipmentsView, self).__call__()

    def folderitems(self):
        items = super(ShipmentsView, self).folderitems()
        for x in range(len(items)):
            if not items[x].has_key('obj'):
                continue
            obj = items[x]['obj']
            items[x]['ShipmentID'] = obj.getId()
            if self.context.portal_type == 'Shipments':
                items[x]['replace']['Project'] = "<a href='%s'>%s</a>" % \
                                                 (obj.aq_parent.absolute_url(),
                                                  obj.aq_parent.Title())
            items[x]['ShippingDate'] = self.ulocalized_time(
                obj.getShippingDate())
            items[x]['Courier'] = obj.getCourier()
            items[x]['replace']['ShipmentID'] = "<a href='%s'>%s</a>" % \
                                                (items[x]['url'],
                                                 obj.getId())
        return items
