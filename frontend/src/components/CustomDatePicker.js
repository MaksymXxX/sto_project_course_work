import React, { useState, useEffect, useRef } from 'react';
import api from '../utils/api';
import { translations } from '../translations/translations';

const CustomDatePicker = ({ value, onChange, disabled, availableDates = [], selectedService = null, excludeAppointmentId = null, onDateSelect = null, language = 'uk' }) => {
  const [currentMonth, setCurrentMonth] = useState(() => {
    const now = new Date();
    return new Date(now.getFullYear(), now.getMonth(), 1);
  });
  const [isOpen, setIsOpen] = useState(false);
  const [availableDatesList, setAvailableDatesList] = useState([]);
  const calendarRef = useRef(null);
  const inputRef = useRef(null);
  const [openUp, setOpenUp] = useState(false);
  const [dropdownMaxHeight, setDropdownMaxHeight] = useState(undefined);

  useEffect(() => {
    const fetchAvailableDates = async () => {
      if (!selectedService || !selectedService.id) return;

      try {
        let url = `/api/boxes/available_dates/?service_id=${selectedService.id}`;
        if (excludeAppointmentId) {
          url += `&exclude_appointment_id=${excludeAppointmentId}`;
        }
        const response = await api.get(url);
        const dates = response.data.available_dates || [];
        setAvailableDatesList(dates);
      } catch (error) {
        console.error('Помилка завантаження доступних дат:', error);
        setAvailableDatesList([]);
      }
    };

    if (!disabled && availableDates.length === 0) {
      fetchAvailableDates();
    } else {
      setAvailableDatesList(availableDates);
    }
  }, [disabled, availableDates, selectedService, excludeAppointmentId]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (calendarRef.current && !calendarRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    const recalcDropdownPosition = () => {
      if (!inputRef.current) return;
      const rect = inputRef.current.getBoundingClientRect();
      const viewportHeight = window.innerHeight || document.documentElement.clientHeight;
      const spaceBelow = Math.max(0, viewportHeight - rect.bottom);
      const spaceAbove = Math.max(0, rect.top);
      const desiredHeight = 360; // approximate desired dropdown height
      const shouldOpenUp = spaceBelow < desiredHeight && spaceAbove > spaceBelow;
      setOpenUp(shouldOpenUp);
      const availableSpace = shouldOpenUp ? spaceAbove - 12 : spaceBelow - 12;
      const maxByViewport = Math.max(200, Math.min(availableSpace, Math.round(viewportHeight * 0.8)));
      setDropdownMaxHeight(maxByViewport);
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      window.addEventListener('resize', recalcDropdownPosition);
      window.addEventListener('scroll', recalcDropdownPosition, true);
      recalcDropdownPosition();
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      window.removeEventListener('resize', recalcDropdownPosition);
      window.removeEventListener('scroll', recalcDropdownPosition, true);
    };
  }, [isOpen]);

  const getDaysInMonth = (date) => {
    const year = date.getFullYear();
    const month = date.getMonth();

    // Перший день місяця
    const firstDayOfMonth = new Date(year, month, 1);

    // Останній день місяця
    const lastDayOfMonth = new Date(year, month + 1, 0);
    const daysInMonth = lastDayOfMonth.getDate();

    // День тижня для першого дня місяця (0 = неділя, 1 = понеділок, ...)
    const startingDayOfWeek = firstDayOfMonth.getDay();

    const days = [];

    // Додаємо пусті дні для початку місяця
    for (let i = 0; i < startingDayOfWeek; i++) {
      days.push(null);
    }

    // Додаємо дні місяця
    for (let i = 1; i <= daysInMonth; i++) {
      days.push(new Date(year, month, i));
    }

    return days;
  };

  const isDateAvailable = (date) => {
    if (!date) return false;
    // Використовуємо локальну дату замість UTC
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const dateStr = `${year}-${month}-${day}`;
    return availableDatesList.includes(dateStr);
  };

  const isDateDisabled = (date) => {
    if (!date) return true;
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const isPast = date < today;
    const isAvailable = isDateAvailable(date);
    return isPast || !isAvailable;
  };

  const handleDateClick = (date) => {
    if (date && !isDateDisabled(date)) {
      // Використовуємо локальну дату замість UTC
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      const dateStr = `${year}-${month}-${day}`;

      // Викликаємо onChange з правильним об'єктом події
      if (onChange) {
        onChange({ target: { name: 'appointment_date', value: dateStr } });
      }

      // Викликаємо onDateSelect callback якщо він переданий
      if (onDateSelect && selectedService) {
        onDateSelect(dateStr, selectedService);
      }

      setIsOpen(false);
    }
  };

  const formatDisplayDate = (date) => {
    if (!date) return '';
    const locale = language === 'en' ? 'en-US' : 'uk-UA';
    return date.toLocaleDateString(locale, {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const nextMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 1));
  };

  const prevMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1, 1));
  };

  const monthNames = language === 'en' ? [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ] : [
    'Січень', 'Лютий', 'Березень', 'Квітень', 'Травень', 'Червень',
    'Липень', 'Серпень', 'Вересень', 'Жовтень', 'Листопад', 'Грудень'
  ];

  const days = getDaysInMonth(currentMonth);

  return (
    <div className="custom-date-picker" ref={calendarRef}>
      <input
        type="text"
        className="form-control"
        value={value ? formatDisplayDate(new Date(value)) : ''}
        onClick={() => {
          if (!disabled) {
            setIsOpen(!isOpen);
          }
        }}
        ref={inputRef}
        readOnly
        disabled={disabled}
        placeholder={translations.select_date_placeholder[language]}
        style={{
          opacity: disabled ? 0.6 : 1,
          cursor: disabled ? 'not-allowed' : 'pointer'
        }}
      />

      {isOpen && !disabled && (
        <div
          className="date-picker-dropdown"
          style={{
            top: openUp ? 'auto' : '100%',
            bottom: openUp ? '100%' : 'auto',
            maxHeight: dropdownMaxHeight ? `${dropdownMaxHeight}px` : undefined,
            overflowY: 'auto'
          }}
        >
          <div className="date-picker-header">
            <button type="button" onClick={prevMonth} className="month-nav-btn">
              &lt;
            </button>
            <span className="current-month">
              {monthNames[currentMonth.getMonth()]} {currentMonth.getFullYear()}
            </span>
            <button type="button" onClick={nextMonth} className="month-nav-btn">
              &gt;
            </button>
          </div>

          <div className="date-picker-calendar">
            <div className="calendar-weekdays">
              <div>{translations.sunday_short[language]}</div>
              <div>{translations.monday_short[language]}</div>
              <div>{translations.tuesday_short[language]}</div>
              <div>{translations.wednesday_short[language]}</div>
              <div>{translations.thursday_short[language]}</div>
              <div>{translations.friday_short[language]}</div>
              <div>{translations.saturday_short[language]}</div>
            </div>

            <div className="calendar-days">
              {days.map((day, index) => {
                // Використовуємо локальну дату для порівняння
                const dayDateStr = day ? `${day.getFullYear()}-${String(day.getMonth() + 1).padStart(2, '0')}-${String(day.getDate()).padStart(2, '0')}` : '';

                return (
                  <div
                    key={index}
                    className={`calendar-day ${!day ? 'empty' :
                      isDateDisabled(day) ? 'disabled' :
                        value === dayDateStr ? 'selected' : 'available'
                      }`}
                    onClick={() => handleDateClick(day)}
                  >
                    {day ? day.getDate() : ''}
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CustomDatePicker;