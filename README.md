# Mobile Employee Directory

![Odoo 18.0](https://img.shields.io/badge/Odoo-18.0-714B67) ![License LGPL-3](https://img.shields.io/badge/license-LGPL--3-blue) ![Version 18.0.1.0.0](https://img.shields.io/badge/version-18.0.1.0.0-informational)

> Employee directory (call, e-mail) and org chart in the MobileDoo app.

Odoo 18 addon of [MobileDoo](https://github.com/MobileDoo) (`mobile_hr`).

## Overview

Employee directory and organisation chart for the MobileDoo app: look a colleague up, call, message or e-mail them in one tap, and
walk the reporting line. It reads `hr.employee.public`, the view of colleagues Odoo already allows every internal user to see, so
**no private HR data is exposed**.

## Features

- Searchable directory: by name, job title, department, e-mail or phone number.
- Scopes `all` and `department` (the user's department and its sub-departments).
- Employee card and profile with work location, company, coach, and the management chain from the top down to the direct manager,
  plus direct reports.
- Photos served by the core's image route with the user's own read rights; no photo returns 404 and the app shows initials.
- Home tile, quick action and tab entry named *Directory*.

## Requirements

| | |
|---|---|
| Odoo | 18.0 (Community or Enterprise) |
| Odoo modules | `hr` |
| MobileDoo addons | [`mobile_connector`](https://github.com/MobileDoo/mobile_connector/tree/18.0) (same branch) |
| Client | the [MobileDoo](https://github.com/MobileDoo) app for Android and iPhone |

This branch targets **Odoo 18** only; use the branch of your Odoo version.

## Installation

```bash
git clone --branch 18.0 https://github.com/MobileDoo/mobile_hr.git
git clone --branch 18.0 https://github.com/MobileDoo/mobile_connector.git
# add the cloned folders to addons_path in odoo.conf, then:
odoo -d <database> -i mobile_hr --stop-after-init
```

The addon is the `mobile_hr/` folder at the root of the repository, so the repository folder itself can go on `addons_path`.

`auto_install` is set: Odoo installs `mobile_hr` by itself as soon as all its dependencies are installed, so putting the folders on `addons_path` and updating the Apps list is enough.

To upgrade after pulling a newer version: `odoo -d <database> -u mobile_hr --stop-after-init`.

## How it works

| Piece | Technical detail |
|---|---|
| Record service | `employees` on `hr.employee.public` (`mobile.employee.service`, extends `mobile.record.service`) |
| Capability | `employees.view`, granted to internal users who can read `hr.employee.public` |
| Endpoint | `POST /mobile/api/v1/employees/profile` with `{"id"?}` returns `{employee, managers, reports, reports_total}`; without `id` it returns the caller |
| Lists | `POST /mobile/api/v1/records/employees/list` with `{"scope": "all" | "department", "query"?, "offset"?, "limit"?}` |
| Images | `GET /mobile/api/v1/image/hr.employee.public/<id>/image_128|256|512?v=<image_version>` |

`employee` carries `work_location`, `company`, `coach` and `is_me`. `managers` is ordered from the top of the hierarchy to the direct
manager; `reports` are the direct reports only.

## Security

The addon declares no groups, access rules or data of its own. Visibility follows the standard Odoo rights on
`hr.employee.public`: a user who cannot read it gets no `employees` capability and the routes answer `403 feature_denied`.

## Extending

Override `_mobile_domain(scope, params)` on `mobile.employee.service` to narrow the directory (for example to one company), or
`_mobile_search_domain` to search more fields. Extra fields for the card come from *Mobile App > Extra Fields* without code.

```python
class MobileEmployeeService(models.AbstractModel):
    _inherit = 'mobile.employee.service'

    @api.model
    def _mobile_domain(self, scope, params):
        return super()._mobile_domain(scope, params) + [('company_id', '=', self.env.company.id)]
```

## Contributing

Issues and pull requests are welcome. Open pull requests against the branch of the Odoo version you are fixing (this one is `18.0`) and
keep the change inside the `mobile_hr/` folder.

These repositories are published from MobileDoo's development repository, which remains the source of truth. A merged pull request is
taken back there, and the branches of the other Odoo versions are updated by the maintainers, so a fix is usually welcome even if you can
only test it on one version. `README.md` and `LICENSE` are generated at each release; changes to them are not carried back.

## License

LGPL-3: see [LICENSE](LICENSE).
