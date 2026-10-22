from odoo import _, api, models


class MobileApi(models.AbstractModel):
    _inherit = 'mobile.api'

    @api.model
    def _mobile_features(self):
        return super()._mobile_features() + ['employees']

    @api.model
    def _mobile_record_services(self):
        return dict(super()._mobile_record_services(), employees='mobile.employee.service')

    @api.model
    def _mobile_access(self):
        access = super()._mobile_access()
        # hr.employee.public: what every internal user may see of colleagues (no private data).
        if not self.env.user.share and self.env['hr.employee.public'].check_access_rights('read', raise_exception=False):
            access['employees'] = {'view': True}
        return access

    @api.model
    def _mobile_home_tiles(self):
        return super()._mobile_home_tiles() + [
            {'key': 'employees', 'label': _('Directory'), 'feature': 'employees', 'capability': None, 'sequence': 40},
        ]

    @api.model
    def _mobile_home_shortcuts(self):
        return super()._mobile_home_shortcuts() + [
            {'key': 'employees', 'label': _('Directory'), 'feature': 'employees', 'capability': None},
        ]

    @api.model
    def _mobile_home_tabs(self):
        return super()._mobile_home_tabs() + [
            {'key': 'employees', 'label': _('Directory'), 'feature': 'employees', 'capability': None, 'sequence': 80},
        ]
