from odoo import http
from odoo.http import request

from odoo.addons.mobile_connector.controllers.utils import MobileApiError, get_record, mobile_route, require_access


class MobileEmployeeController(http.Controller):

    @mobile_route('/mobile/api/v1/employees/profile')
    def profile(self, payload):
        """A colleague's card and place in the org chart (`id` omitted: the user's own)."""
        require_access('employees')
        if payload.get('id'):
            employee = get_record('hr.employee.public', payload['id'])
        else:
            own = request.env.user.employee_id
            if not own:
                raise MobileApiError('missing', 'You have no employee record in this company.', 404)
            employee = request.env['hr.employee.public'].browse(own.id)
        return request.env['mobile.employee.service']._mobile_profile(employee)
