from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button

from kivy.uix.scrollview import ScrollView

from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.properties import *

from kivy.config import ConfigParser
from kivy.uix.settings import Settings, SettingOptions


from mytrip.db import DB
from mytrip.data import Place,Location


#list of open itmems
#@todo specify filter and ordering of Place data
#@todo consistency check in Settings screen (check if one can already predefined a valid range in the JSON file)
#@todo impolement in DetailScreen a Delete and a Cancel Button
#@todo implement MapsView of Offline Maps in PlaceDetail

#/// load template file for screen design ///
Builder.load_file('mytrip.kv') #it is essential to call Builder explicitely when working with Screens !!!


class PlaceSettingScreen(Screen):
    placeid = NumericProperty(0)
    def __init__(self, placeid, **kwargs):
        super(PlaceSettingScreen,self).__init__(**kwargs)
        self.data = None
        self.placeid = placeid

        self.draw()


    def update(self):

        self.clear_widgets()

        #define structure of fields (like an INI file)
        config = ConfigParser()
        config.add_section('general')
        config.add_section('location')
        config.add_section('icon_file')

        #--- set values (needs to come from database) todo
        #config.set('general','place_name','Name of the place: ' + str(self.placeid))
        if self.data == None:
            config.set('location','lat','Enter lat here')
            config.set('location','lon','This is a dummy lon.')

            config.set('general','place_name','This is a dummy which should never be seen')
            config.set('general','category_name','This is a dummy which should never be seen')
            config.set('general','ranking','This is a dummy which should never be seen')
            config.set('general','visited','This is a dummy which should never be seen')
            config.set('icon_file','icon_file','This is a dummy which should never be seen')
        else:
            place = self.data
            config.set('location','lat',place.lat)
            config.set('location','lon',place.lon)

            config.set('general','place_name',place.name)

            config.set('general','category_name',place.cat_name )
            config.set('general','ranking', self._ranking2str(place.stars))
            config.set('general','visited',place.status)
            config.set('icon_file','icon_file','Testpath') #todo:how to deal with image data ???

        return config

    def _ranking2str(self,n):
        """
        convert the ranking from DB into a string
        """
        s = ''
        if n <= 0:
            s = 'unspecified'
        else:
            for i in range(n):
                s += '*'
        return s

    def _str2ranking(self,s):
        return len(s)


    def _get_category_widget(self):
        #return widget which contains category information
        panel=self._get_panel()

        for c in panel.children:
            print c
            if isinstance(c,SettingOptions):
                if c.key == 'category_name':
                    return c
        return None


    def _get_catname_list(self):
        """
        get a name of categories as a list
        """
        cl = db.get_categories()
        res = []
        for id in cl.keys():
            res.append(cl[id]['name'])
        res.sort()
        return res



    def draw(self):

        config = self.update()

        #--- specify settings screen from file
        self.settings = Settings()
        self.settings.add_json_panel('Settings', config, filename='setting_place.json') #todo: do not read this from file, but from string

        cat_widget = self._get_category_widget()
        cat_widget.options = self._get_catname_list() #get list of category names from DB

        #--- add widget ---
        self.add_widget(self.settings)

        btn_close = self.settings.children[1].children[0] #todo this is not so good if it is hardwired like this!
        btn_close.bind(on_press=self.close)


    def close(self,touch):
        self._save()

        s = sm.get_screen('mainscreen')
        s.data = db.get_places()
        s.update()

        sm.current = 'mainscreen'

    def _get_panel(self):
        k = self.settings._panels.keys()
        if len(k) != 1:
            raise ValueError, 'Expecting a single entry here!'
        panel = self.settings._panels[k[0]][0]
        return panel

    def _save(self):
        """
        save current setting to database
        """
        panel = self._get_panel()

        lat  = panel.get_value('location','lat')
        lon  = panel.get_value('location','lon')
        name = panel.get_value('general','place_name')
        ranking = panel.get_value('general','ranking')
        stars = self._str2ranking(ranking)

        status = panel.get_value('general','visited')
        cat_name = panel.get_value('general','category_name')

        #--- save Location information ---
        if self.placeid < 1:
            placeid = None
        else:
            placeid = self.placeid
        L = Location(placeid,lat,lon,name,stars,status)
        db.save_location(L)
        if placeid is None:
            L.id = db._get_last_key('Location')[0] #id of location

        #--- save Category information
        db.save_place(L.id,self._categoryname2id(cat_name))

    def _categoryname2id(self,name):
        c = db.get_categories()
        for k in c.keys():
            if c[k]['name'] == name:
                return k

        return 0







class CategorySettingScreen(Screen):
    catid = NumericProperty(0)
    data  = ObjectProperty(None)
    def __init__(self, catid, **kwargs):
        super(CategorySettingScreen,self).__init__(**kwargs)
        self.catid = catid
        x = self.data
        self.draw()

    def update(self):
        """
        add data to Category settings

        retrieves data from database for a particular 'catid'
        """
        #/// add data ///

        self.clear_widgets()

        #define structure of fields (like an INI file)
        config = ConfigParser()
        config.add_section('category')
        config.add_section('icon_file')

        #--- set values (needs to come from database)
        #config.set('category','category_name','TestnameID: ' + str(self.catid))
        if self.data == None:
            config.set('category','category_name','Enter your category name here')
        else:
            config.set('category','category_name',self.data['name'])
        config.set('icon_file','icon_file','Testpath') #todo:how to deal with image data ???

        return config


    def draw(self):

        config = self.update()

        #--- specify settings screen from file
        self.settings = Settings()
        self.settings.add_json_panel('Settings', config, filename='setting_category.json') #todo: do not read this from file, but from string

        #--- add widget ---
        self.add_widget(self.settings)

        btn_close = self.settings.children[1].children[0] #todo this is not so good if it is hardwired like this!
        btn_close.bind(on_press=self.close)


    def close(self,touch):
        #save results in database
        self._save()

        #update category list in main category screen
        s = sm.get_screen('catscreen')
        s.data = db.get_categories()
        s.update()

        #set focus
        sm.current = 'catscreen'

    def _get_panel(self):
        k = self.settings._panels.keys()
        if len(k) != 1:
            raise ValueError, 'Expecting a single entry here!'
        panel = self.settings._panels[k[0]][0]
        return panel

    def _save(self):
        """
        save current setting to database
        """
        panel = self._get_panel()
        db.save_category(panel.get_value('category','category_name'),self.catid)





















class MarketSettingScreen(Screen):
    marketid = NumericProperty(0)
    data  = ObjectProperty(None)
    def __init__(self, marketid, **kwargs):
        super(MarketSettingScreen,self).__init__(**kwargs)
        self.marketid = marketid
        x = self.data
        self.draw()


    def _str2ranking(self,s):
        return len(s)


    def update(self):
        """
        add data to Category settings

        retrieves data from database for a particular 'catid'
        """
        #/// add data ///

        self.clear_widgets()

        #define structure of fields (like an INI file)
        config = ConfigParser()
        config.add_section('market')
        config.add_section('location')

        #--- set values (needs to come from database)
        #config.set('category','category_name','TestnameID: ' + str(self.catid))
        if self.data == None:
            config.set('market','day','Enter the market DAY here')
            config.set('location','lon','enter longitude here')
            config.set('location','lat','enter latitude here')
            config.set('location','place_name','enter place name here')
            config.set('location','ranking','Ranking here')
            config.set('location','visited',False)
        else:
            config.set('market','day',self.data['day'])

        return config


    def draw(self):

        config = self.update()

        #--- specify settings screen from file
        self.settings = Settings()
        self.settings.add_json_panel('Settings', config, filename='setting_market.json') #todo: do not read this from file, but from string

        #--- add widget ---
        self.add_widget(self.settings)

        btn_close = self.settings.children[1].children[0] #todo this is not so good if it is hardwired like this!
        btn_close.bind(on_press=self.close)


    def close(self,touch):
        #save results in database
        self._save()

        #update category list in main category screen
        s = sm.get_screen('marketscreen')
        s.data = db.get_markets()
        s.update()

        #set focus
        sm.current = 'marketscreen'

    def _get_panel(self):
        k = self.settings._panels.keys()
        if len(k) != 1:
            raise ValueError, 'Expecting a single entry here!'
        panel = self.settings._panels[k[0]][0]
        return panel

    def _save(self):
        """
        save current setting to database
        """
        panel = self._get_panel()

        lat  = panel.get_value('location','lat')
        lon  = panel.get_value('location','lon')
        name = panel.get_value('location','place_name')
        ranking = panel.get_value('location','ranking')
        stars = self._str2ranking(ranking)
        status = panel.get_value('location','visited') #todo this might cuase trouble if the same Location is used for markets and other things !!!

        #--- save Location information ---
        if self.marketid < 1:  #new market
            placeid = None
        else:
            placeid = self.placeid
        L = Location(placeid,lat,lon,name,stars,status)
        db.save_location(L)
        if placeid is None:
            L.id = db._get_last_key('Location')[0] #id of location

        #--- save Category information
        db.save_place(L.id,0) #todo: might cause trouble when using same Location data for different categories !!!


        db.save_market(panel.get_value('market','day'),self.marketid, L.id)
































class ToolBar(Widget):
    def __init__(self,**kwargs):
        super(ToolBar,self).__init__(**kwargs)

    def add_new(self):
        """
        add a new dataset. Dependent on the current screen,
        this is one of the following options
        a) Place
        b) Category
        c) Market
        """

        if sm.current_screen.name == 'mainscreen':
            s = sm.get_screen('placedetails')
            s.placeid = -99
            s.data = None
            s.draw()
            sm.current = 'placedetails'


        elif sm.current_screen.name == 'catscreen':
            s = sm.get_screen('catdetails')
            s.catid = -99
            s.data = None
            s.draw()
            sm.current = 'catdetails'



            print 'new category screen will be called'
        elif sm.current_screen.name == 'marketscreen':
            s = sm.get_screen('marketdetails')
            s.catid = -99
            s.data = None
            s.draw()
            sm.current = 'marketdetails'
        else:
            return







class FilterScreen(Screen):
    pass




class SearchScreen(Screen):
    pass


class ItemButton(Button):
    """
    implements a button with a title and a text
    """

    id_value = NumericProperty(0)

    def __init__(self, title,content,**kwargs):
        super(ItemButton,self).__init__(**kwargs)

        color_visited = '00ff00'
        color_not_visited = 'ff0000'
        color_neutral = 'ffffff'

        if 'visited' in kwargs.keys():
            if kwargs['visited'] is not None:
                if kwargs['visited']:
                    color = color_visited
                else:
                    color = color_not_visited
            else:
                color = color_neutral
        else:
            color = color_neutral


        #red: ff0000
        #green: 00ff00

        self.markup = True
        self.text = '[color=' + color + '][b][i]' + title + '[/i][/b][/color]'
        if content is not None:
            self.text = self.text + '\n' + '[size=10]' + content + '[/size]'
        self.size_hint_y=None

        #self.add_widget(Image(source='icons/like.png',x=self.parent.x + self.parent.width*0.1, y = self.parent.y + self.parent.height*0.5,size=(25,25),allow_stretch = True))

        #todo: relative Layout
        #~ im = Image(source='icons/test1.png',pos=self.center)   #todo: how to make this scrollable ???
        #~ self.add_widget(im)


class ItemScreen(Screen):

    type = ObjectProperty(None)

    def __init__(self, data, **kwargs):
        super(ItemScreen, self).__init__(**kwargs)
        self.data = data
        self.update()

    def update(self):

        self.clear_widgets()
        self.add_widget(ToolBar()) #todo: relative layout !

        scroll_layout = GridLayout(cols=1, spacing=1, size_hint_y=None)
        scroll_layout.bind(minimum_height=scroll_layout.setter('height'))

        if isinstance(self.data,list):
            for d in self.data:
                btn = self.get_button(d)
                btn.bind(on_press=self.open_detail)
                scroll_layout.add_widget(btn)
        else: #otherwise assume that it is a dictionary with an ID field
            for id in self.data.keys():
                btn = self.get_button(id)
                #btn = ItemButton(self.type.upper() + ' ' + str(d),'Subtitle string ....', size_hint_y=None, height=40,id_value=d) #IMPORTANT for scroll_view to have size_hint!!!
                #btn.add_widget(Image(source='icons/like.png',allow_stretch = True, size=(25,25), x = btn.x + btn.width*0.1, y=btn.y + btn.height*0.5))
                btn.bind(on_press=self.open_detail) #gives id
                scroll_layout.add_widget(btn)
        scroll_vw = ScrollView(size_hint=(None, None), size=(800, 500)) #todo: how to set this height relative ???
        scroll_vw.add_widget(scroll_layout)
        self.add_widget(scroll_vw)

    def open_detail(self,btn):
        """
        opens a detail screen
        """
        pass
        #~ raise ValueError, 'You should not end here! Implement this routine in the subclass!'


    def get_button(self,i):
        """
        get button; dependent on the subclass, this can be done in different ways
        (e.g. using different database queries); implement this function in the subclasses!

        @param d: specifies a coutner to access the data in self.data
        """
        return Button(text='This is a dummy button!',size_hint_y=None, height=40)


class CatScreen(ItemScreen):
    def __init__(self, **kwargs):
        self.type = 'category'
        data = self.get_data()
        super(CatScreen, self).__init__(data,**kwargs)

    def get_button(self,id):
        """
        set Button properties for Categories

        @param i: a counter to access an entry in self.data as obtained from db.get_categories(); {'id':id,'name':name}
        @type i: int
        """
        btn = ItemButton(self.data[id]['name'],'Subtitle string for category ...', size_hint_y=None, height=40,id_value=id) #IMPORTANT for scroll_view to have size_hint!!!
        return btn

    def open_detail(self,btn):
        """
        opens a detail screen

        btn: Button object
        """
        s = sm.get_screen('catdetails')
        s.catid = btn.id_value
        s.data  = self.data[btn.id_value] #set data so it can be used for details
        s.draw()
        sm.current = 'catdetails'

    def get_data(self):
        return db.get_categories()


class PlaceScreen(ItemScreen):
    def __init__(self, **kwargs):
        self.type = 'place'
        data = db.get_places()
        super(PlaceScreen, self).__init__(data,**kwargs)

    def get_button(self,id):
        """
        @param place: Place which specifies location
        @type place: C{Place}
        """

        place = self.data[id]

        if not isinstance(place,Place):
            raise ValueError, 'Place instance expected here!'
        btn = ItemButton(place.name,'Subtitle string for place ....', size_hint_y=None, height=40,id_value=place.id,visited=place.status) #IMPORTANT for scroll_view to have size_hint!!!
        return btn


    def open_detail(self,btn):
        """
        opens a detail screen

        btn: Button object
        """
        s = sm.get_screen('placedetails')
        s.placeid = btn.id_value
        s.data = self.data[btn.id_value] #gives a Place object
        s.draw()
        sm.current = 'placedetails'

class MarketScreen(ItemScreen):
    def __init__(self, **kwargs):
        self.type = 'market'
        data = self.get_data()
        super(MarketScreen, self).__init__(data,**kwargs)

    def get_button(self,id):
        """
        set Button properties for Categories

        @param i: a counter to access an entry in self.data as obtained from db.get_categories(); {'id':id,'name':name}
        @type i: int
        """
        btn = ItemButton('Market location ID: ' + str(self.data[id]['loc_id']),'Market on ' + str(self.data[id]['weekday']), size_hint_y=None, height=40,id_value=id) #IMPORTANT for scroll_view to have size_hint!!!
        return btn

    def xxxxxxopen_detail(self,btn):
        """
        opens a detail screen

        btn: Button object
        """
        s = sm.get_screen('catdetails')
        s.catid = btn.id_value
        s.data  = self.data[btn.id_value] #set data so it can be used for details
        s.draw()
        sm.current = 'catdetails'

    def get_data(self):
        return db.get_markets()


#~ todo: automatic change with data content ???

#~ im = Image(source='icons/test1.png',pos=self.center)   #todo: how to make this scrollable ???


#--- open database file ---
db = DB(file='./data/mytrip.db')

# --- Create the screen manager ---
sm = ScreenManager()
sm.add_widget(PlaceScreen(name='mainscreen'))
sm.add_widget(CategorySettingScreen(0,name='catdetails'))
sm.add_widget(PlaceSettingScreen(0,name='placedetails'))
sm.add_widget(MarketSettingScreen(0,name='marketdetails'))

sm.add_widget(CatScreen(name='catscreen'))
sm.add_widget(FilterScreen(name='filterscreen'))
sm.add_widget(MarketScreen(name='marketscreen'))
sm.add_widget(SearchScreen(name='searchscreen'))


#retrieve options from panel in PlaceDetails ???


#~
#x = CatScreen()
#stop


class TestApp(App):
    def build(self):
        return sm
        #return ItemScreen()
        #~ return CategorySettingScreen(5)


if __name__ == '__main__':
    TestApp().run()
