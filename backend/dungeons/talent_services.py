from .models import UserTalent

class TalentService:
    @staticmethod
    def get_user_talents(user):
        return UserTalent.objects.filter(user=user)

    @staticmethod
    def apply_talent_effects(user, base_stats):
        talents = TalentService.get_user_talents(user)
        modified_stats = base_stats.copy()

        for user_talent in talents:
            talent = user_talent.talent
            for bonus in talent.rank_bonuses:
                stat = bonus.get('stat')
                value = bonus.get('value')
                if stat and value:
                    if stat in modified_stats:
                        modified_stats[stat] += value * user_talent.rank
                    else:
                        modified_stats[stat] = value * user_talent.rank
        
        return modified_stats
