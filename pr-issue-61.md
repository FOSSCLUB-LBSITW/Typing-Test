## 📌 Description
Implemented functionality that allows the user to start the typing test by pressing the `Enter` (`<Return>`) key instead of clicking the "Start Test" button with the mouse. This enables a more seamless and intuitive typing test workflow without taking hands off the keyboard.

## 🔗 Related Issue
Closes #61

## 🛠 Changes Made
- Bound the `<Return>` key to check if `self.start_button` is enabled.
- Invokes `self.start_test()` if it is safe to start the test.

## 📷 Screenshots (if applicable)

## ✅ Checklist
- [x] I have tested my changes
- [x] I have linked the related issue
- [x] My code follows project guidelines
