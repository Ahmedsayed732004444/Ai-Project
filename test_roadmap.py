"""
Test script for roadmap generation endpoint.
Run this to verify the /generate-roadmap endpoint works correctly.
"""

import sys
import json
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.services.roadmap_service import generate_roadmap


async def test_roadmap_generation():
    """Test roadmap generation with sample user data."""
    
    print("=" * 70)
    print("Testing Roadmap Generation Service")
    print("=" * 70)
    
    # Sample user data (similar to Ahmed's profile)
    sample_user_data = {
        "personal_info": {
            "full_name": "Ahmed Elsayed",
            "email": "ahmedsayed732004@gmail.com",
            "phone": "+201062885633",
            "location": "Tanta, Egypt"
        },
        "summary": (
            "Ambitious software engineer aiming to apply problem-solving "
            "and teamwork skills to deliver high-quality software solutions "
            "while continuing to learn and grow in the tech industry."
        ),
        "skills": [
            "C#", "OOP", "ASP.NET Core", "Web API", ".NET Framework",
            "SQL Server", "LINQ", "Entity Framework", "EF Core", "ADO.NET",
            "Problem Solving", "Data Structures", "Algorithms",
            "SOLID", "Design Patterns", "Git", "GitHub",
            "GitHub Actions", "Docker"
        ],
        "education": [
            {
                "degree": "Bachelor's Degree",
                "field": "Computer Science",
                "institution": "The Egyptian E-Learning University",
                "year": "Oct 2022 - Jul 2026"
            }
        ],
        "experience": [],
        "certifications": [],
        "languages": ["Arabic", "English"]
    }
    
    test_user_id = "test-user-123"
    
    print("\n📊 User Data Summary:")
    print(f"   Name: {sample_user_data['personal_info']['full_name']}")
    print(f"   Skills: {len(sample_user_data['skills'])} skills")
    print(f"   Experience: {len(sample_user_data['experience'])} entries")
    print(f"   Education: {len(sample_user_data['education'])} entries")
    
    print("\n🤖 Calling AI to generate roadmap...")
    print("   (This may take 5-15 seconds)")
    
    try:
        roadmap = await generate_roadmap(sample_user_data, test_user_id)
        
        print("\n✅ SUCCESS - Roadmap generated!")
        print("=" * 70)
        
        # Display results
        print(f"\n📅 Duration: {roadmap.roadmap_duration}")
        print(f"🎯 Total Phases: {len(roadmap.roadmap)}")
        
        print("\n" + "=" * 70)
        print("ROADMAP DETAILS")
        print("=" * 70)
        
        for idx, phase in enumerate(roadmap.roadmap, 1):
            print(f"\n🔹 {phase.phase}")
            print(f"   └─ Focus Areas ({len(phase.focus)}):")
            for focus_item in phase.focus:
                print(f"      • {focus_item}")
            
            print(f"   └─ Topics to Learn ({len(phase.topics)}):")
            for topic in phase.topics[:3]:  # Show first 3
                print(f"      • {topic}")
            if len(phase.topics) > 3:
                print(f"      ... and {len(phase.topics) - 3} more topics")
            
            print(f"   └─ Projects ({len(phase.projects)}):")
            for project in phase.projects:
                print(f"      • {project}")
        
        print("\n" + "=" * 70)
        print("MERMAID DIAGRAM CODE")
        print("=" * 70)
        print(roadmap.mermaid_code)
        
        print("\n" + "=" * 70)
        print("COMPLETE JSON RESPONSE")
        print("=" * 70)
        
        # Convert to dict for pretty printing
        roadmap_dict = {
            "userId": roadmap.userId,
            "roadmap_duration": roadmap.roadmap_duration,
            "roadmap": [
                {
                    "phase": p.phase,
                    "focus": p.focus,
                    "topics": p.topics,
                    "projects": p.projects
                }
                for p in roadmap.roadmap
            ],
            "mermaid_code": roadmap.mermaid_code
        }
        
        print(json.dumps(roadmap_dict, indent=2, ensure_ascii=False))
        
        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED!")
        print("=" * 70)
        
        # Save to file for inspection
        output_file = Path(__file__).parent / "sample_roadmap_output.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(roadmap_dict, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Sample output saved to: {output_file}")
        
        return True
        
    except Exception as exc:
        print("\n❌ FAILED - Error generating roadmap")
        print(f"   Error: {exc}")
        import traceback
        traceback.print_exc()
        return False


async def test_error_cases():
    """Test error handling."""
    print("\n" + "=" * 70)
    print("Testing Error Cases")
    print("=" * 70)
    
    # Test 1: Empty data
    print("\n🧪 Test 1: Empty user data")
    try:
        await generate_roadmap({}, "test-user")
        print("   ⚠️  Should have failed but didn't")
    except Exception as exc:
        print(f"   ✅ Correctly handled: {type(exc).__name__}")
    
    # Test 2: Minimal data
    print("\n🧪 Test 2: Minimal user data")
    minimal_data = {
        "skills": ["Python"],
        "education": [],
        "experience": []
    }
    try:
        roadmap = await generate_roadmap(minimal_data, "minimal-user")
        print(f"   ✅ Generated roadmap with {len(roadmap.roadmap)} phases")
    except Exception as exc:
        print(f"   ⚠️  Failed: {exc}")


def main():
    """Run all tests."""
    print("\n" + "🚀" * 35)
    print("ROADMAP GENERATION - TEST SUITE")
    print("🚀" * 35)
    
    # Check GROQ_API_KEY
    from app.core.config import settings
    if not settings.groq_api_key:
        print("\n❌ ERROR: GROQ_API_KEY not set in .env")
        print("   Please add your API key from https://console.groq.com")
        return
    
    print(f"\n✅ GROQ_API_KEY configured")
    print(f"✅ Using model: {settings.groq_model}")
    
    # Run tests
    loop = asyncio.get_event_loop()
    
    success = loop.run_until_complete(test_roadmap_generation())
    
    if success:
        loop.run_until_complete(test_error_cases())
    
    print("\n" + "🎉" * 35)
    print("TEST SUITE COMPLETE")
    print("🎉" * 35 + "\n")


if __name__ == "__main__":
    main()
