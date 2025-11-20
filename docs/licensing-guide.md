# Licensing Guide

This document explains the Watchtower Community License and how to apply copyright headers.

---

## License Overview

Watchtower is licensed under the **Watchtower Community License 1.0**, a source-available, non-commercial, no-competition license.

### What You Can Do

✅ **Personal Use** - Use Watchtower for your own projects and infrastructure
✅ **Internal Business Use** - Deploy within your organization for internal monitoring
✅ **View Source** - Read and study the source code
✅ **Modify** - Make changes for your internal use

### What You Cannot Do

❌ **Redistribute** - Share or distribute the software or modifications
❌ **Commercial Use** - Sell or monetize Watchtower without a commercial license
❌ **SaaS/Hosting** - Offer Watchtower as a hosted service
❌ **Competitive Products** - Use Watchtower to build competing products
❌ **Remove Attribution** - Remove or alter copyright notices

---

## Commercial Licensing

If you need to:
- Redistribute Watchtower or modified versions
- Offer Watchtower as a SaaS or managed service
- Integrate Watchtower into commercial products
- Use for consulting or managed security services
- Build on Watchtower for commercial purposes

**Contact:** jfreymann@gmail.com for commercial licensing options.

---

## Copyright Headers

### For Python Files

Add this header to the top of all `.py` files:

```python
#!/usr/bin/env python3
# Copyright © 2025 Jaye Freymann / The Watchtower Project
#
# This file is part of Watchtower, licensed under the Watchtower Community License 1.0.
# You may not use this file except in compliance with the License.
# See LICENSE.md for details.
#
# For commercial licensing: jfreymann@gmail.com
```

### For Markdown Files

Add this notice at the end of documentation files:

```markdown
---

© 2025 Jaye Freymann / The Watchtower Project
Licensed under the Watchtower Community License 1.0
```

### For Configuration Files

For YAML, TOML, or other config files:

```yaml
# Copyright © 2025 Jaye Freymann / The Watchtower Project
# Licensed under the Watchtower Community License 1.0
```

---

## Applying Headers to Existing Files

Use this script to add headers to all Python files:

```bash
#!/bin/bash
HEADER='#!/usr/bin/env python3
# Copyright © 2025 Jaye Freymann / The Watchtower Project
#
# This file is part of Watchtower, licensed under the Watchtower Community License 1.0.
# You may not use this file except in compliance with the License.
# See LICENSE.md for details.
#
# For commercial licensing: jfreymann@gmail.com
'

for file in $(find . -name "*.py" -not -path "./.venv/*" -not -path "./venv/*"); do
    if ! grep -q "Copyright.*Watchtower" "$file"; then
        echo "Adding header to $file"
        echo "$HEADER" | cat - "$file" > temp && mv temp "$file"
    fi
done
```

---

## Contributing

### Contributor License Agreement

By contributing to Watchtower, you agree that:

1. Your contributions are your original work
2. You grant the project perpetual rights to use your contributions
3. Your contributions will be licensed under the Watchtower Community License 1.0
4. You retain copyright to your contributions
5. The project may relicense or dual-license in the future

### Pull Requests

All PRs must:
- Include proper copyright headers
- Not violate the license terms
- Maintain attribution and notices
- Be compatible with the project license

---

## Third-Party Dependencies

Watchtower uses several open-source components under permissive licenses (MIT, Apache 2.0, BSD).

See [NOTICE](../NOTICE) for the complete list of dependencies and their licenses.

All third-party licenses are compatible with the Watchtower Community License.

---

## FAQ

### Can I use Watchtower in my company?

Yes, for internal monitoring and security purposes. You cannot offer it as a service to others or build a competing product.

### Can I modify the code?

Yes, for internal use only. You cannot distribute your modifications.

### Can I fork the repository?

Public forks are allowed for contribution purposes only. You cannot distribute binaries, containers, or run a public fork as a competing project.

### What if I want to offer Watchtower as a service?

Contact jfreymann@gmail.com for a commercial license.

### Can I use Watchtower in open-source projects?

Only if those projects are also for personal/internal use and not distributed as SaaS or commercial offerings.

### Can I contribute to the project?

Yes! Contributions are welcome. See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

---

## License Compliance Checklist

Before using Watchtower, ensure you:

- [ ] Are using it for personal or internal business use only
- [ ] Are not redistributing the software or modified versions
- [ ] Are not offering it as a commercial service or SaaS
- [ ] Are not using it to build competing products
- [ ] Have preserved all copyright and license notices
- [ ] Understand the no-warranty terms
- [ ] Have obtained a commercial license if needed

---

## Contact

**Licensing Questions:** jfreymann@gmail.com
**Project Repository:** https://github.com/jfreymann/watchtower
**License File:** [LICENSE.md](../LICENSE.md)

---

© 2025 Jaye Freymann / The Watchtower Project
Licensed under the Watchtower Community License 1.0
