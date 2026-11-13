# Architecture

```text
CLI -> Services -> Repositories -> JSON
          |
        Models
```

- **Models:** بيانات User/Student/Course/Enrollment.
- **Repositories:** القراءة والكتابة فقط.
- **Services:** قواعد العمل والتحقق والتقارير.
- **CLI:** إدخال المستخدم وعرض النتائج.
- **Core:** الإعدادات والاستثناءات والأمن.
- **Utils:** decorators والدوال الوظيفية والتنسيق.

## Dependency Injection
الخدمات تستقبل repositories في constructor بدل إنشائها داخليًا، مما يسهل الاختبار.

## ملاحظة تعليمية
الهدف هو فهم بنية المشروع وكيف تتعاون الطبقات، وليس بناء نظام إنتاجي كامل.
