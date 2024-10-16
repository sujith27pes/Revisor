from flet import *
import math as m
import json
from random import randint as r
from random import choice as chooseOneFrom

class HomePage(Column):
    global testsTaken
    def __init__(self, page: Page):
        super().__init__()
        self.expand = True
        self.testsTaken = 0
        self.avgScore = 0
        self.history = [0,]
        self.avgScore = (m.fsum(self.history)/(len(self.history)-1)) if len(self.history)>1 else 0
        self.mainRing = ProgressRing(width=256,height=256,stroke_width=50, value=self.avgScore/100)
        self.quickInfo = Stack(
            controls=[
                Container(content=Text(f"{self.avgScore}%",size=80,weight="bold"),width=256,height=256,alignment=alignment.center),
                self.mainRing,
            ],
            expand=1
        )

        self.overallinfo = Column(
            spacing=-0,
            controls=[
                Text("Tests taken",size=32),
                Text(f"{self.testsTaken}",color="#66f9f9",size=64, weight="bold")
            ]
        )

        self.QuickInfoRow = Container(padding=Padding(top=100,bottom=0,left=0,right=0),content=Row(
            
            controls=[
                Container(content=self.quickInfo,alignment=alignment.center),
                self.overallinfo,
            ],
            alignment=MainAxisAlignment.CENTER,
            spacing=100
        ))

        data = [LineChartData(
                data_points=[LineChartDataPoint(i,self.history[i]) for i in range(len(self.history))],
                stroke_width=4,
                color= colors.with_opacity(0.5,"#66f9f9"),
                below_line_bgcolor=colors.with_opacity(0.2,"#66f9f9"),
                curved=True,
                stroke_cap_round=True
            )]

        self.progressChart = LineChart(
            horizontal_grid_lines=ChartGridLines(24),
            height=200,
            data_series=data,
            left_axis=ChartAxis(
                labels_interval=1,
                labels=[
                    ChartAxisLabel(value=0,label=Text("0%")),
                    ChartAxisLabel(value=25,label=Text("25%")),
                    ChartAxisLabel(value=50,label=Text("50%")),
                    ChartAxisLabel(value=75,label=Text("75%")),
                    ChartAxisLabel(value=100,label=Text("100%")),
                ],
                labels_size=40
            ),
            bottom_axis=ChartAxis(
                labels_interval=1,
                labels=[ChartAxisLabel(value=10*i,label=Text(str(10*i))) for i in range(1,(m.ceil(self.testsTaken/10))+1)],
                labels_size=32,
            ),
            min_y=0, min_x=0,max_y=100,
            animate=1000,
            expand=False
        )
        self.progressChart.data_series[0].point = False
        self.alignment = MainAxisAlignment.SPACE_BETWEEN
        self.controls=[ 
            self.QuickInfoRow,
            self.progressChart
        ]
    def generateXlables(self):
        upper = m.ceil(self.testsTaken/10)
        return [ChartAxisLabel(value=10*i,label=Text(str(10*i))) for i in range(1,upper+1)]

        

                                                                                
                                                                                





class MaterialsPage(Column):
    def __init__(self,page:Page):
        super().__init__()
        self.visible = False
        if page.client_storage.contains_key("stat.totalQs"):
            self.length = page.client_storage.get("stat.totalQs")
        else:
            page.client_storage.set('all_tags',[])
            page.client_storage.set("stat.totalQs",0)
            page.client_storage.set('bank',[])
            self.update()
        self.uploadForm = Container(
            content=Row(
                controls=[
                    TextField(
                        label="Add MCQs (JSON)",
                        expand=1,
                        border_color="#FFFFFF",
                        multiline=True,
                    ),
                    FloatingActionButton(icon=icons.ADD, on_click=self.addMCQ)
                ],
                alignment=MainAxisAlignment.CENTER
            ),
            alignment=alignment.center
        )

        self.bankSize = Column(
            spacing=0,
            controls=[
                Container(content=Text(f"{self.length}",color="#66f9f9",size=96, weight="bold"),alignment=alignment.center),
                Container(content=Text("MCQs",size=16),alignment=alignment.center),
            ],
            alignment=MainAxisAlignment.CENTER
            
        )

        self.bankDisplay = Container(
            content=self.bankSize,
            alignment=alignment.center,
            expand=True
        )

        self.controls = [
            self.uploadForm,
            self.bankDisplay
        ]     
        self.expand = True

    

    def addMCQ(self,e):
        self.fullBank = self.page.client_storage.get("bank")
        self.all_tags = self.page.client_storage.get("all_tags")

        self.MCQ_objects = [json.loads(i) for i in self.uploadForm.content.controls[0].value.splitlines()]
        for mcq_obj in self.MCQ_objects:
            for i in mcq_obj["t"]:
                if i not in self.all_tags:
                    self.all_tags.append(i)
            self.page.client_storage.set("all_tags",self.all_tags)
            self.fullBank.append(mcq_obj)
        print([type(i) for i in self.fullBank])
        self.page.client_storage.set("bank",self.fullBank)
        self.uploadForm.content.controls[0].value=''
        self.length += len(self.MCQ_objects)
        self.bankSize.controls[0].content.value = f'{self.length}'
        self.page.client_storage.set("stat.totalQs", self.length)
        self.page.update()




class Tags(Chip):
    def __init__(self,label,):
        super().__init__(label=label)
        self.disabled_color = colors.TRANSPARENT
        self.bgcolor = colors.TRANSPARENT
        self.disabled = False
        self.on_select = self.toggle
        self.selected = False
        self.show_checkmark = False
    
    def toggle(self,e):
        pass


class MCQ(Container):
    def __init__(self,q,t,o,a):
        super().__init__()
        self.border_radius = 30
        self.padding = Padding(top=32,left=32, right=32, bottom= 32)
        self.margin = Margin(left=24,top=24,right=24,bottom=24)
        self.bgcolor = colors.BLACK54
        self.Options = RadioGroup(
                    content=Column(
                        [
                            Radio(value=0,label=o[0]),
                            Radio(value=1,label=o[1]),
                            Radio(value=2,label=o[2]),
                            Radio(value=3,label=o[3]),
                        ]
                    )
                )
        self.content = Column(
            controls=[
                Text(value=q,size=32,color='#66f9f9'),
                self.Options
            ]
        )



class TestPage(Column):
    def __init__(self,page:Page):
        super().__init__()
        self.visible = False
        self.all_tags = page.client_storage.get("all_tags")
        self.question_bank = page.client_storage.get("bank")
        self.selected_tags = []
        self.expand = True

        self.totalTestQs = 10
        self.Temp1 = r(6,10)
        self.Temp2 = self.totalTestQs - self.Temp1
        self.TestMix = [self.Temp1,self.Temp2,0]
        self.horizontal_alignment = MainAxisAlignment.SPACE_AROUND

        self.question_paper = []


        self.tagChips = [Tags(label=Text(i)) for i in self.all_tags]
        self.tagsSheet = BottomSheet(
            dismissible=True,
                content= Container(
                    expand=True,
                    content= Row(
                        tight=True,
                        controls=self.tagChips
                    ),
                ),
                on_dismiss = self.tagsSet
            )


        self.testModes = Container(
            alignment=alignment.center,
            content=Row(controls=[
                            SegmentedButton(
                                selected_icon=Icon(icons.RADIO_BUTTON_ON),
                                allow_multiple_selection=False,
                                selected="q",
                                segments=[
                                    Segment(
                                        value="q",
                                        label=Text("Quick"),
                                        icon=Icon(icons.RADIO_BUTTON_OFF)
                                    ),
                                    Segment(
                                        value="b",
                                        label=Text("Bundle"),
                                        icon=Icon(icons.RADIO_BUTTON_OFF),
                                    )
                                ],
                                on_change=self.select_testMode
                            ),
                            SegmentedButton(
                                selected_icon=Icon(icons.RADIO_BUTTON_ON),
                                allow_multiple_selection=False,
                                selected="e",
                                segments=[
                                    Segment(
                                        value="e",
                                        label=Text("Easy"),
                                        icon=Icon(icons.RADIO_BUTTON_OFF)
                                    ),
                                    Segment(
                                        value="m",
                                        label=Text("Medium"),
                                        icon=Icon(icons.RADIO_BUTTON_OFF)
                                    ),
                                    Segment(
                                        value="h",
                                        label=Text("Hard"),
                                        icon=Icon(icons.RADIO_BUTTON_OFF)
                                    )
                                ],
                                on_change=self.select_testDifficulty
                            ),
                            FilledButton(
                                text="Generate Test",
                                on_click=self.generateTest
                            ),
                            IconButton(icon=icons.SETTINGS,on_click=self.tagsSelection)
                        ],
                        alignment=MainAxisAlignment.CENTER
                    ),

                
            )
        


        self.testArea = Container(
            alignment=alignment.center,
            margin=Margin(0,0,0,50),
            content= Column(
                controls=self.question_paper,
                horizontal_alignment=MainAxisAlignment.START,
            )
        )
        self.scroll = ScrollMode.AUTO
        self.controls = [
            self.testModes,
            self.testArea,
            ElevatedButton(text="hello")
        ]
    


    def generateTest(self,e):
        # say testMix = [6,2,2]
        if self.totalTestQs == 10:
            i=0
            while i < self.TestMix[0]:
                tempMCQ = chooseOneFrom(self.question_bank)
                if "easy" in tempMCQ["t"] and self.selected_tags in tempMCQ["t"]:
                    self.question_paper.append
                    i += 1
        pass




    def select_testMode(self,e):
        if self.testModes.content.controls[0].selected == {'q'}:
            self.totalTestQs = 10
        if self.testModes.content.controls[0].selected == {'b'}:
            self.totalTestQs = 30
        self.update()

    def select_testDifficulty(self,e):
        print(e)
        if self.testModes.content.controls[1].selected == {"e"}:
            self.Temp1 = r(6,10)
            self.Temp2 = self.totalTestQs - self.Temp1
            self.TestMix = [self.Temp1,self.Temp2,0]
            print(self.TestMix)
        if self.testModes.content.controls[1].selected == {'m'}:
            self.Temp1 = r(6,10)
            self.Temp2 = self.totalTestQs - self.Temp1
            self.TestMix = [self.Temp2//2,self.Temp1,self.Temp2 - self.Temp2//2]
            print(self.TestMix)
        if self.testModes.content.controls[1].selected == {'h'}:
            self.Temp1 = r(6,8)
            self.Temp2 = self.totalTestQs - self.Temp1
            self.TestMix = [0,self.Temp2,self.Temp1]
            print(self.TestMix)



    def tagsSelection(self,e):
        self.all_tags = self.page.client_storage.get("all_tags")
        self.page.open(self.tagsSheet)
        self.tagsSheet.update()
    
    def tagsSet(self,e):
        for i in self.tagChips:
            print(i.selected)
            if i.selected and i.label.value not in self.selected_tags:
                self.selected_tags.append(i.label.value)
            if not i.selected and i.label.value in self.selected_tags:
                self.selected_tags.remove(i.label.value)
        self.page.update()
        print(self.selected_tags)
























def main(page: Page):
    page.title = "Revisor"
    page.theme = Theme(color_scheme_seed="#66f9f9",font_family="Bahnschrift")

    def switichTabs(e):
        if e.control.selected_index == 0:
            home.visible = True
            mats.visible = False
            test.visible = False
        elif e.control.selected_index == 1:
            home.visible = False
            mats.visible = True
            test.visible = False
        elif e.control.selected_index == 2:
            home.visible = False
            mats.visible = False
            test.visible = True
        page.update()


    rail = NavigationRail(
        selected_index=0,
        label_type=NavigationRailLabelType.ALL,
        # extended=True,
        min_width=100,
        min_extended_width=400,
        leading=FloatingActionButton(bgcolor=colors.TRANSPARENT,content=Image(src="./assets/goggles.svg",scale=1.5)),
        group_alignment=-0.9,
        destinations=[
            NavigationRailDestination(
                icon=icons.BUBBLE_CHART_OUTLINED, selected_icon=icons.BUBBLE_CHART_ROUNDED, label="Performance"
            ),
            NavigationRailDestination(
                icon=icons.FOLDER_OUTLINED, selected_icon=icons.FOLDER_ROUNDED, label="Material"
            ),
            NavigationRailDestination(
                icon_content=Icon(icons.EDIT_NOTE_ROUNDED),
                selected_icon_content=Icon(icons.EDIT_DOCUMENT),
                label="Test",
            ),
            NavigationRailDestination(
                icon=icons.SETTINGS_OUTLINED,
                selected_icon_content=Icon(icons.SETTINGS),
                label_content=Text("Settings"),
            ),
        ],
        on_change=switichTabs,
    )

    home = HomePage(page)
    mats = MaterialsPage(page)
    test = TestPage(page)
    page.add(
        Row(
            [
                rail,
                VerticalDivider(width=1),
                Column([
                    home,
                    mats,
                    test
                ], 
                alignment=MainAxisAlignment.SPACE_BETWEEN, 
                expand=True,),
            ],
            expand=True,
        )
    )

app(target=main)

