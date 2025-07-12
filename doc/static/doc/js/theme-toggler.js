/*!
 * Color mode toggler for Bootstrap's docs (https://getbootstrap.com/)
 * Copyright 2011-2025 The Bootstrap Authors
 * Licensed under the Creative Commons Attribution 3.0 Unported License.
 */

(() => {
  'use strict'

  const getStoredTheme = () => localStorage.getItem('theme')
  const setStoredTheme = theme => localStorage.setItem('theme', theme)

  const getPreferredTheme = () => {
    const storedTheme = getStoredTheme()
    if (storedTheme) {
      return storedTheme
    }

    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  }

  const setTheme = theme => {
    if (theme === 'auto') {
      document.documentElement.setAttribute('data-bs-theme', (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'))
    } else {
      document.documentElement.setAttribute('data-bs-theme', theme)
    }
  }

  setTheme(getPreferredTheme())

  const showActiveTheme = (theme, focus = false) => {
      const themeToggleBtn = document.querySelector('#bd-theme')
      const themeToggleText = document.querySelector('#bd-theme-text')
      const activeThemeBtn = document.querySelector(`[data-bs-theme-value="${theme}"]`)
      const activeIconClass = activeThemeBtn?.querySelector('i')?.className

      if (!themeToggleBtn || !activeThemeBtn || !activeIconClass) return

      // Vorhandenes Icon im Toggle-Button entfernen (falls vorhanden)
      const existingIcon = themeToggleBtn.querySelector('i')
      if (existingIcon) existingIcon.remove()

      // Neues Icon aus aktivem Button klonen und einsetzen
      const newIcon = document.createElement('i')
      newIcon.className = activeIconClass
      newIcon.classList.add('me-2')  // optionaler Abstand
      themeToggleBtn.insertBefore(newIcon, themeToggleText)

      // Optional: aktive Klasse setzen
      document.querySelectorAll('[data-bs-theme-value]').forEach(el => {
        el.classList.remove('active')
        el.setAttribute('aria-pressed', 'false')
      })
      activeThemeBtn.classList.add('active')
      activeThemeBtn.setAttribute('aria-pressed', 'true')

      if (focus) themeToggleBtn.focus()
    }

  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
    const storedTheme = getStoredTheme()
    if (storedTheme !== 'light' && storedTheme !== 'dark') {
      setTheme(getPreferredTheme())
    }
  })

  window.addEventListener('DOMContentLoaded', () => {
    showActiveTheme(getPreferredTheme())
    document.querySelectorAll('[data-bs-theme-value]')
      .forEach(toggle => {
        toggle.addEventListener('click', () => {
          const theme = toggle.getAttribute('data-bs-theme-value')
          setStoredTheme(theme)
          setTheme(theme)
          showActiveTheme(theme, true)
        })
      })
  })
})()