#!/usr/bin/env python3
"""
Calendar Event Manager

A production-ready Python module for managing calendar events, detecting overlaps,
and suggesting optimal rescheduling solutions.

Author: Claude
Date: 2026-02-12
"""

from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Tuple, Optional, Set
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Priority(Enum):
    """Event priority levels for rescheduling decisions."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class CalendarEvent:
    """
    Represents a calendar event with start/end times and metadata.
    
    Attributes:
        id: Unique identifier for the event
        title: Event title/description
        start_time: Event start datetime
        end_time: Event end datetime
        priority: Event priority level for rescheduling decisions
        is_movable: Whether this event can be rescheduled
        duration_minutes: Calculated duration in minutes
    """
    id: str
    title: str
    start_time: datetime
    end_time: datetime
    priority: Priority = Priority.MEDIUM
    is_movable: bool = True
    
    def __post_init__(self) -> None:
        """Validate event data after initialization."""
        if self.start_time >= self.end_time:
            raise ValueError(f"Event {self.id}: start_time must be before end_time")
        
    @property
    def duration_minutes(self) -> int:
        """Calculate event duration in minutes."""
        return int((self.end_time - self.start_time).total_seconds() / 60)
    
    def overlaps_with(self, other: 'CalendarEvent') -> bool:
        """
        Check if this event overlaps with another event.
        
        Args:
            other: Another CalendarEvent to check against
            
        Returns:
            True if events overlap, False otherwise
        """
        return (self.start_time < other.end_time and 
                self.end_time > other.start_time)


@dataclass
class TimeSlot:
    """
    Represents a free time slot for scheduling.
    
    Attributes:
        start_time: Slot start datetime
        end_time: Slot end datetime
        duration_minutes: Calculated duration in minutes
    """
    start_time: datetime
    end_time: datetime
    
    @property
    def duration_minutes(self) -> int:
        """Calculate slot duration in minutes."""
        return int((self.end_time - self.start_time).total_seconds() / 60)
    
    def can_fit_event(self, event: CalendarEvent) -> bool:
        """Check if an event can fit in this time slot."""
        return self.duration_minutes >= event.duration_minutes


@dataclass
class RescheduleSuggestion:
    """
    Represents a suggestion to reschedule an event.
    
    Attributes:
        event: The event to be rescheduled
        original_slot: Original time slot
        suggested_slot: Suggested new time slot
        confidence_score: Confidence in this suggestion (0-100)
        reason: Human-readable reason for the suggestion
    """
    event: CalendarEvent
    original_slot: TimeSlot
    suggested_slot: TimeSlot
    confidence_score: int
    reason: str


class CalendarManager:
    """
    Manages calendar events, detects overlaps, and suggests optimal rescheduling.
    
    This class provides comprehensive calendar management functionality including
    overlap detection, conflict resolution, and intelligent rescheduling suggestions.
    """
    
    def __init__(self, events: Optional[List[CalendarEvent]] = None):
        """
        Initialize the calendar manager.
        
        Args:
            events: Optional initial list of calendar events
        """
        self.events: List[CalendarEvent] = events or []
        logger.info(f"CalendarManager initialized with {len(self.events)} events")
    
    def add_event(self, event: CalendarEvent) -> None:
        """
        Add an event to the calendar.
        
        Args:
            event: CalendarEvent to add
        """
        if any(e.id == event.id for e in self.events):
            raise ValueError(f"Event with ID {event.id} already exists")
        
        self.events.append(event)
        logger.info(f"Added event: {event.title} ({event.id})")
    
    def remove_event(self, event_id: str) -> bool:
        """
        Remove an event from the calendar.
        
        Args:
            event_id: ID of the event to remove
            
        Returns:
            True if event was removed, False if not found
        """
        initial_count = len(self.events)
        self.events = [e for e in self.events if e.id != event_id]
        removed = len(self.events) < initial_count
        
        if removed:
            logger.info(f"Removed event: {event_id}")
        else:
            logger.warning(f"Event not found: {event_id}")
        
        return removed
    
    def detect_overlaps(self) -> List[Tuple[CalendarEvent, CalendarEvent]]:
        """
        Detect all overlapping event pairs.
        
        Returns:
            List of tuples containing overlapping event pairs
        """
        overlaps = []
        
        for i, event1 in enumerate(self.events):
            for event2 in self.events[i + 1:]:
                if event1.overlaps_with(event2):
                    overlaps.append((event1, event2))
        
        logger.info(f"Detected {len(overlaps)} overlapping event pairs")
        return overlaps
    
    def find_free_slots(self, 
                       start_date: datetime, 
                       end_date: datetime,
                       min_duration_minutes: int = 30,
                       working_hours_only: bool = True) -> List[TimeSlot]:
        """
        Find free time slots within a date range.
        
        Args:
            start_date: Start of the search period
            end_date: End of the search period
            min_duration_minutes: Minimum slot duration to consider
            working_hours_only: If True, only consider 9 AM - 6 PM slots
            
        Returns:
            List of available TimeSlot objects
        """
        if start_date >= end_date:
            raise ValueError("start_date must be before end_date")
        
        # Get all events within the date range, sorted by start time
        relevant_events = [
            e for e in self.events 
            if e.start_time < end_date and e.end_time > start_date
        ]
        relevant_events.sort(key=lambda e: e.start_time)
        
        free_slots = []
        current_time = start_date
        
        for event in relevant_events:
            # Check if there's a gap before this event
            gap_start = max(current_time, start_date)
            gap_end = min(event.start_time, end_date)
            
            if gap_end > gap_start:
                slot = TimeSlot(gap_start, gap_end)
                if slot.duration_minutes >= min_duration_minutes:
                    if not working_hours_only or self._is_working_hours(slot):
                        free_slots.append(slot)
            
            # Update current time to end of this event
            current_time = max(current_time, event.end_time)
        
        # Check for a final gap after the last event
        if current_time < end_date:
            slot = TimeSlot(current_time, end_date)
            if slot.duration_minutes >= min_duration_minutes:
                if not working_hours_only or self._is_working_hours(slot):
                    free_slots.append(slot)
        
        logger.info(f"Found {len(free_slots)} free slots between {start_date} and {end_date}")
        return free_slots
    
    def suggest_rescheduling(self, 
                           search_days_ahead: int = 7,
                           working_hours_only: bool = True) -> List[RescheduleSuggestion]:
        """
        Suggest optimal rescheduling for overlapping events.
        
        Args:
            search_days_ahead: Number of days to search for alternative slots
            working_hours_only: If True, only suggest slots during working hours
            
        Returns:
            List of RescheduleSuggestion objects
        """
        overlaps = self.detect_overlaps()
        if not overlaps:
            logger.info("No overlaps detected, no rescheduling needed")
            return []
        
        suggestions = []
        
        # Calculate search period
        earliest_overlap = min(min(pair[0].start_time, pair[1].start_time) for pair in overlaps)
        search_start = earliest_overlap
        search_end = search_start + timedelta(days=search_days_ahead)
        
        # Process each overlapping pair
        conflicting_events: Set[str] = set()
        for event1, event2 in overlaps:
            conflicting_events.add(event1.id)
            conflicting_events.add(event2.id)
        
        # Find events that should be rescheduled (movable, lower priority)
        events_to_reschedule = []
        for event_id in conflicting_events:
            event = next(e for e in self.events if e.id == event_id)
            if event.is_movable:
                events_to_reschedule.append(event)
        
        # Sort by priority (lower priority first) and duration (shorter first)
        events_to_reschedule.sort(key=lambda e: (e.priority.value, e.duration_minutes))
        
        # Find suitable slots for each event to reschedule
        for event in events_to_reschedule:
            free_slots = self.find_free_slots(
                search_start, 
                search_end, 
                event.duration_minutes,
                working_hours_only
            )
            
            # Score each slot based on various factors
            best_slot = None
            best_score = 0
            
            for slot in free_slots:
                if slot.can_fit_event(event):
                    score = self._calculate_slot_score(event, slot)
                    if score > best_score:
                        best_score = score
                        best_slot = slot
            
            if best_slot:
                original_slot = TimeSlot(event.start_time, event.end_time)
                suggestion = RescheduleSuggestion(
                    event=event,
                    original_slot=original_slot,
                    suggested_slot=best_slot,
                    confidence_score=min(best_score, 100),
                    reason=self._generate_reschedule_reason(event, best_slot, best_score)
                )
                suggestions.append(suggestion)
        
        logger.info(f"Generated {len(suggestions)} rescheduling suggestions")
        return suggestions
    
    def _is_working_hours(self, slot: TimeSlot) -> bool:
        """Check if a time slot falls within working hours (9 AM - 6 PM)."""
        slot_start_hour = slot.start_time.hour
        slot_end_hour = slot.end_time.hour
        
        # Simple check: slot must start at or after 9 AM and end by 6 PM
        return (slot_start_hour >= 9 and 
                (slot_end_hour < 18 or (slot_end_hour == 18 and slot.end_time.minute == 0)))
    
    def _calculate_slot_score(self, event: CalendarEvent, slot: TimeSlot) -> int:
        """
        Calculate a score for how suitable a slot is for an event.
        
        Higher scores indicate better suitability.
        """
        score = 50  # Base score
        
        # Prefer slots that are similar time of day to original
        original_hour = event.start_time.hour
        slot_hour = slot.start_time.hour
        hour_diff = abs(original_hour - slot_hour)
        score -= hour_diff * 2  # Penalty for different times
        
        # Prefer slots that are close to the original date
        days_diff = abs((slot.start_time.date() - event.start_time.date()).days)
        score -= days_diff * 5  # Penalty for different dates
        
        # Prefer slots with similar duration (avoid too much extra time)
        duration_efficiency = event.duration_minutes / slot.duration_minutes
        if duration_efficiency > 0.8:  # Good fit
            score += 20
        elif duration_efficiency > 0.5:  # Acceptable fit
            score += 10
        
        # Prefer working hours
        if self._is_working_hours(slot):
            score += 15
        
        return max(0, score)
    
    def _generate_reschedule_reason(self, event: CalendarEvent, slot: TimeSlot, score: int) -> str:
        """Generate a human-readable reason for a reschedule suggestion."""
        reasons = []
        
        if score > 80:
            reasons.append("Excellent match")
        elif score > 60:
            reasons.append("Good alternative time")
        else:
            reasons.append("Available slot found")
        
        # Add specific reasons based on slot characteristics
        if self._is_working_hours(slot):
            reasons.append("during working hours")
        
        days_diff = (slot.start_time.date() - event.start_time.date()).days
        if days_diff == 0:
            reasons.append("on the same day")
        elif days_diff == 1:
            reasons.append("next day")
        elif days_diff <= 3:
            reasons.append("within a few days")
        
        return ", ".join(reasons) + "."
    
    def get_calendar_summary(self) -> dict:
        """
        Get a summary of the calendar state.
        
        Returns:
            Dictionary containing calendar statistics
        """
        overlaps = self.detect_overlaps()
        
        summary = {
            "total_events": len(self.events),
            "overlapping_pairs": len(overlaps),
            "conflicted_events": len(set(e.id for pair in overlaps for e in pair)),
            "movable_events": len([e for e in self.events if e.is_movable]),
            "priority_breakdown": {
                priority.name: len([e for e in self.events if e.priority == priority])
                for priority in Priority
            }
        }
        
        if self.events:
            summary["earliest_event"] = min(e.start_time for e in self.events)
            summary["latest_event"] = max(e.end_time for e in self.events)
        
        return summary


def main():
    """
    Example usage and testing of the CalendarManager.
    """
    print("Calendar Manager - Example Usage")
    print("=" * 40)
    
    # Create sample events
    now = datetime.now()
    
    events = [
        CalendarEvent(
            id="meeting1",
            title="Team Standup",
            start_time=now.replace(hour=9, minute=0, second=0, microsecond=0),
            end_time=now.replace(hour=9, minute=30, second=0, microsecond=0),
            priority=Priority.HIGH,
            is_movable=False
        ),
        CalendarEvent(
            id="meeting2", 
            title="Project Review",
            start_time=now.replace(hour=9, minute=15, second=0, microsecond=0),
            end_time=now.replace(hour=10, minute=0, second=0, microsecond=0),
            priority=Priority.MEDIUM,
            is_movable=True
        ),
        CalendarEvent(
            id="meeting3",
            title="Client Call", 
            start_time=now.replace(hour=14, minute=0, second=0, microsecond=0),
            end_time=now.replace(hour=15, minute=0, second=0, microsecond=0),
            priority=Priority.HIGH,
            is_movable=True
        ),
        CalendarEvent(
            id="meeting4",
            title="Code Review",
            start_time=now.replace(hour=14, minute=30, second=0, microsecond=0),
            end_time=now.replace(hour=15, minute=30, second=0, microsecond=0),
            priority=Priority.LOW,
            is_movable=True
        )
    ]
    
    # Initialize calendar manager
    calendar = CalendarManager(events)
    
    # Display calendar summary
    summary = calendar.get_calendar_summary()
    print(f"\nCalendar Summary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    # Detect overlaps
    print(f"\nDetecting Overlaps:")
    overlaps = calendar.detect_overlaps()
    for event1, event2 in overlaps:
        print(f"  CONFLICT: '{event1.title}' overlaps with '{event2.title}'")
    
    # Get rescheduling suggestions
    print(f"\nRescheduling Suggestions:")
    suggestions = calendar.suggest_rescheduling()
    
    if suggestions:
        for i, suggestion in enumerate(suggestions, 1):
            print(f"  {i}. Reschedule '{suggestion.event.title}'")
            print(f"     From: {suggestion.original_slot.start_time.strftime('%H:%M')} - {suggestion.original_slot.end_time.strftime('%H:%M')}")
            print(f"     To: {suggestion.suggested_slot.start_time.strftime('%H:%M')} - {suggestion.suggested_slot.end_time.strftime('%H:%M')}")
            print(f"     Confidence: {suggestion.confidence_score}%")
            print(f"     Reason: {suggestion.reason}")
            print()
    else:
        print("  No rescheduling suggestions available.")
    
    # Find free slots
    print(f"\nFree Slots Today:")
    today_start = now.replace(hour=8, minute=0, second=0, microsecond=0)
    today_end = now.replace(hour=18, minute=0, second=0, microsecond=0)
    
    free_slots = calendar.find_free_slots(today_start, today_end)
    for slot in free_slots[:5]:  # Show first 5 slots
        print(f"  {slot.start_time.strftime('%H:%M')} - {slot.end_time.strftime('%H:%M')} ({slot.duration_minutes} minutes)")


if __name__ == "__main__":
    main()