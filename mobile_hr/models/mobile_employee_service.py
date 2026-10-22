"""Employee directory and org chart.

Built on `hr.employee.public`, Odoo's own "what colleagues may see" model:
no private data (address, salary...) ever reaches the app, and multi-company
record rules apply.
"""
from odoo import api, fields, models

MAX_MANAGER_LEVELS = 10
MAX_REPORTS = 200


class MobileEmployeeService(models.AbstractModel):
    _name = 'mobile.employee.service'
    _inherit = 'mobile.record.service'
    _description = 'Mobile Employee Directory'

    _mobile_model = 'hr.employee.public'
    _mobile_feature = 'employees'
    _mobile_create_capability = None
    _mobile_scope_capabilities = {'all': 'view', 'department': 'view'}
    _mobile_core_field_names = [
        'name', 'job_title', 'department_id', 'parent_id', 'coach_id', 'work_email', 'work_phone',
        'mobile_phone', 'work_location_id', 'company_id',
    ]
    _mobile_list_field_names = ['name', 'job_title', 'department_id', 'work_email', 'work_phone', 'mobile_phone',
                                'write_date']

    @api.model
    def _mobile_domain(self, scope, params):
        if scope == 'all':
            return []
        if scope == 'department':
            department = self.env.user.employee_id.department_id
            return [('department_id', 'child_of', department.id)] if department else [('id', '=', 0)]
        return super()._mobile_domain(scope, params)

    @api.model
    def _mobile_search_domain(self, query):
        """Name, job, department, e-mail or phone number."""
        return ['|', '|', '|', '|', '|',
                ('name', 'ilike', query), ('job_title', 'ilike', query), ('department_id.name', 'ilike', query),
                ('work_email', 'ilike', query), ('work_phone', 'ilike', query), ('mobile_phone', 'ilike', query)]

    @api.model
    def _mobile_order(self, scope):
        return 'name'

    # ------------------------------------------------------------------
    # Profile + org chart
    # ------------------------------------------------------------------

    @api.model
    def _mobile_card(self, employee):
        return {
            'id': employee.id,
            'name': employee.name,
            'job_title': employee.job_title or False,
            'department': [employee.department_id.id, employee.department_id.display_name]
            if employee.department_id else False,
            'work_email': employee.work_email or False,
            'work_phone': employee.work_phone or False,
            'mobile_phone': employee.mobile_phone or False,
            'has_image': bool(employee.image_128),
            # Changes with the photo: the app uses it as cache key of /image/hr.employee.public/<id>/image_128.
            'image_version': fields.Datetime.to_string(employee.write_date) if employee.write_date else False,
        }

    @api.model
    def _mobile_profile(self, employee):
        """{employee, managers (top -> direct manager), reports (direct), coach}."""
        managers, seen, manager = [], {employee.id}, employee.parent_id
        while manager and manager.id not in seen and len(managers) < MAX_MANAGER_LEVELS:
            managers.insert(0, self._mobile_card(manager))
            seen.add(manager.id)
            manager = manager.parent_id
        reports = employee.child_ids.sorted('name')[:MAX_REPORTS]
        card = self._mobile_card(employee)
        card.update({
            'work_location': [employee.work_location_id.id, employee.work_location_id.display_name]
            if employee.work_location_id else False,
            'company': [employee.company_id.id, employee.company_id.name] if employee.company_id else False,
            'coach': self._mobile_card(employee.coach_id) if employee.coach_id and employee.coach_id != employee.parent_id else False,
            'is_me': employee.user_id == self.env.user,
        })
        return {
            'employee': card,
            'managers': managers,
            'reports': [self._mobile_card(report) for report in reports],
            'reports_total': len(employee.child_ids),
        }
